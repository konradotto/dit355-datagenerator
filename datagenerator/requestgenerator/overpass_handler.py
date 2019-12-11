"""
Script to handle data files produced with overpass.
"""
import uuid
import calendar
import json
from datagenerator.utils import path_utils
import random
from datagenerator.requestgenerator.travel_request import TravelRequest, Issuance, TimeStamp, Coordinate, Device, Purpose, TransportationType
from datagenerator.requestgenerator.geometric_operations import shift_coordinate
import paho.mqtt.client as mqtt  # import the client
import time
import math
import numpy as np
from datetime import datetime
import getopt
import sys


BUS_FILE = path_utils.get_data_path().joinpath('bus_stops_gothenburg.geojson')
SHIFTING_DISTANCE = 500  # meters of shifting distance


def load_geo_features(filename):
    """Opens a json-file containing a list of geo features and returns them as object."""
    with open(filename, encoding='utf-8') as f:
        geo_features: object = json.load(f)
        return geo_features


def extract_coordinate_list(feature_object):
    """Turn a json-object containing features into a list of their coordinates."""
    feature_list = feature_object['features']
    coordinate_list = [(feature['geometry']['coordinates']) for feature in feature_list]
    return coordinate_list


class OverpassHandler:

    def __init__(self, filename: str):
        self.filename = filename
        self.coordinate_list = []
        self.load_coordinate_list()

    def load_coordinate_list(self):
        """Directly extract the coordinates of features from a json-file."""
        self.coordinate_list = extract_coordinate_list(load_geo_features(self.filename))

    def get_coordinates(self):
        return self.coordinate_list


class CoordinatePicker:

    def __init__(self, coordinates):
        self.coordinates = coordinates

    def pick_randomly(self):
        """Pick one of the provided coordinates."""
        coord = random.choice(self.coordinates)
        return Coordinate(coord[1], coord[0])

    def pick_randomly_with_circular_uncertainty(self, uncertainty_distance=SHIFTING_DISTANCE):
        """Pick a coordinate randomly and add uncertainty of upto <distance> meters to it."""
        # make distribution uniform over the area instead of the distance by squaring it
        distance = random.uniform(0, uncertainty_distance ** 2) ** 0.5
        angle_rad = random.uniform(0, 2 * math.pi)

        before_uncertainty = self.pick_randomly()
        with_uncertainty = shift_coordinate(before_uncertainty, angle_rad, distance)  # shift according to uncertainty

        return with_uncertainty


class IdTracker:

    def __init__(self):
        self.current_id = 1

    def next(self):
        result = self.current_id
        self.current_id = self.current_id + 1
        return result


class PurposePicker:

    purposes = [Purpose('work'), Purpose('leisure'), Purpose('school'), Purpose('tourism')]

    def __init__(self, purposes=None, p=None):
        if purposes is not None:
            self.purposes = purposes

        if p is None or len(p) != len(self.purposes):
            p = [1/len(self.purposes) for _ in self.purposes]

        total_likelihood = sum(p)
        self.borders = [likelihood/total_likelihood for likelihood in np.cumsum(p)]

    def pick_random(self):
        rand = np.random.uniform()
        return self.purposes[next(i for i, v in enumerate(self.borders) if v >= rand)]


class DevicePicker:

    def __init__(self, devices):
        self.devices = devices

    def pick_random(self):
        return Device(random.choice(self.devices))


class TransportationTypePicker:

    transportation_types: TransportationType

    def __init__(self, types: TransportationType, p=None):
        if p is None or len(p) != len(types):
            p = [1/len(types) for _ in types]
        self.transportation_types = types
        total_likelihood = sum(p)
        self.borders = [likelihood/total_likelihood for likelihood in np.cumsum(p)]

    def pick_random(self):
        rand = np.random.uniform()
        return self.transportation_types[next(i for i, v in enumerate(self.borders) if v >= rand)]


class RequestCreator:

    def __init__(self, id_tracker: IdTracker, devices, coordinate_picker: CoordinatePicker,
                 purpose_picker: PurposePicker, type_picker: TransportationTypePicker,
                 coordinate_picker_target: CoordinatePicker = None):
        if coordinate_picker_target is None:
            coordinate_picker_target = coordinate_picker

        self.id_tracker = id_tracker
        self.device_picker = DevicePicker(devices)
        self.coordinate_picker_source = coordinate_picker
        self.coordinate_picker_target = coordinate_picker_target
        self.purpose_picker = purpose_picker
        self.transportation_type_picker = type_picker

    def create_random_request(self, uncertainty_distance=SHIFTING_DISTANCE):
        device_id = self.device_picker.pick_random()
        request_id = self.id_tracker.next()
        request_issuance = calendar.timegm(time.gmtime())
        request_source = self.coordinate_picker_source.pick_randomly_with_circular_uncertainty(uncertainty_distance)
        request_target = self.coordinate_picker_target.pick_randomly_with_circular_uncertainty(uncertainty_distance)
        request_timestamp = TimeStamp(datetime.now(), True)
        request_purpose = self.purpose_picker.pick_random()
        transportation_type = self.transportation_type_picker.pick_random()
        return TravelRequest(device_id, request_id, request_issuance, request_source, request_target, request_timestamp,
                             request_purpose, transportation_type)

    def create_timed_request(self, timestamp):
        source = self.picker.pick()
        target = self.picker.pick()
        return TravelRequest(source, target, timestamp)

    def create_issuance_request(self, issuance):
        source = self.picker.pick()
        target = self.picker.pick()
        return TravelRequest(source, target, issuance)


def run(argv):
    # read the passed list of arguments into opts (names) and args (values)
    try:
        opts, args = getopt.getopt(argv, 'i:b:t:c:d:ps:o:', ['ifile', 'broker', 'topic', 'client', 'device', 'print',
                                                             'sleep', 'offset'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)

    # initialise variables that might be set from the cmd
    filename = BUS_FILE
    broker_address = 'localhost'
    client_name = 'random client'
    topic = 'travel_requests'
    device = uuid.getnode()
    do_print = False
    sleep = 0.01
    offset = SHIFTING_DISTANCE

    # parse all command line options into variables
    for opt, arg in opts:
        if opt in ('-i', '--ifile'):
            filename = arg
        elif opt in ('-b', '--broker'):
            broker_address = arg
        elif opt in ('-t', '--topic'):
            topic = arg
        elif opt in ('-c', '--client'):
            client_name = arg
        elif opt in ('-d', '--device'):
            device = arg
        elif opt in ('-p', '--print'):
            do_print = True
            print('Printing mode activated.')
        elif opt in ('-s', '--sleep'):
            try:
                sleep = float(arg)
            except ValueError:
                sys.exit("Sleep time argument [-s]/[--sleep] must be float. Exit.")
        elif opt in ('-o', '--offset'):
            try:
                offset = float(arg)
            except ValueError:
                sys.exit("Offset distance argument [-o]/[--offset] must be float. Exit.")

    # Create a coordinate picker using a file containing coordinates as seeds
    op_handler = OverpassHandler(filename)
    coord_picker = CoordinatePicker(op_handler.get_coordinates())
    trans_type_picker = TransportationTypePicker(["tram", "ferry", "bus"], [0.2, 0.05, 0.75])
    purpose_picker = PurposePicker(p=[5, 3, 1, 1])

    # Create a RequestCreator using random selection for most fields
    travel_request_creator = RequestCreator(IdTracker(), [device], coord_picker, purpose_picker,
                                            trans_type_picker)

    # Set up topic to publish to using mqtt
    client = mqtt.Client(client_name)
    client.connect(broker_address)

    print('Publisher node has been started.')
    print('Publishing to client at: {}'.format(client_name))
    print('Device: \t', device)
    print('Topic: \t\t', topic)
    print('Sleeping {} seconds between messages.'.format(sleep))

    while True:
        """Loop to continuously create and publish requests."""
        req = travel_request_creator.create_random_request(offset)
        client.publish(topic, req.to_json())

        if do_print:
            print(req.to_json())
            print(req.travelRequest['requestId'])

        time.sleep(sleep)