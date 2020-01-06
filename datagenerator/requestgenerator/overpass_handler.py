"""
Script to handle data files produced with overpass.
"""
import uuid
import calendar
import json
from datagenerator.utils import path_utils
import random
from datagenerator.requestgenerator.travel_request import TravelRequest, Issuance, TimeStamp, Coordinate, Device, \
    Purpose, TransportationType
from datagenerator.requestgenerator.geometric_operations import shift_coordinate
import paho.mqtt.client as mqtt  # import the client
import time
import math
import numpy as np
from datetime import datetime, timedelta
import getopt
import sys
import os
from easygui import fileopenbox

BUS_FILE = path_utils.get_data_path().joinpath('bus_stops_gothenburg.geojson')
SHIFTING_DISTANCE = 500  # meters of shifting distance
DEFAULT_OFFSET_DAYS = 7 # length of the interval in generated data


def load_geo_features(filename):
    """Opens a json-file containing a list of geo features and returns them as object."""
    with open(filename, encoding='utf-8') as f:
        geo_features: object = json.load(f)
        return geo_features


def extract_coordinate_list(feature_object, coord_limit=None):
    """Turn a json-object containing features into a list of their coordinates."""
    feature_list = feature_object['features']
    coordinate_list = [(feature['geometry']['coordinates']) for feature in feature_list]
    if coord_limit is not None:
        np.random.shuffle(coordinate_list)
        coordinate_list = coordinate_list[:coord_limit]
    return coordinate_list


def create_empty_file(filename):
    with open(filename, "w"):
        pass


def save_request(request: TravelRequest, filename):
    with open(filename, "a") as file:
        file.write(request.to_numbered_line() + "\n")


def create_random_datetime(max_offset_days: float, before_only: bool = False):
    # do we only want to create random dates which are earlier than now()?
    if before_only:
        offset_days = random.uniform(0, max_offset_days)
    else:
        offset_days = random.uniform(-max_offset_days, max_offset_days)

    return datetime.now() - timedelta(offset_days)


class OverpassHandler:

    def __init__(self, filename: str, coord_limit=None):
        self.filename = filename
        self.coordinate_list = []
        self.load_coordinate_list(coord_limit)

    def load_coordinate_list(self, coord_limit=None):
        """Directly extract the coordinates of features from a json-file."""
        self.coordinate_list = extract_coordinate_list(load_geo_features(self.filename), coord_limit)

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
            p = [1 / len(self.purposes) for _ in self.purposes]

        total_likelihood = sum(p)
        self.borders = [likelihood / total_likelihood for likelihood in np.cumsum(p)]

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
            p = [1 / len(types) for _ in types]
        self.transportation_types = types
        total_likelihood = sum(p)
        self.borders = [likelihood / total_likelihood for likelihood in np.cumsum(p)]

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

    def create_random_request(self, uncertainty_distance=SHIFTING_DISTANCE, max_offset_days=DEFAULT_OFFSET_DAYS):
        device_id = self.device_picker.pick_random()
        request_id = self.id_tracker.next()
        request_issuance = calendar.timegm(time.gmtime())
        request_source = self.coordinate_picker_source.pick_randomly_with_circular_uncertainty(uncertainty_distance)
        request_target = self.coordinate_picker_target.pick_randomly_with_circular_uncertainty(uncertainty_distance)
        request_timestamp = TimeStamp(create_random_datetime(max_offset_days), True)
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
        opts, args = getopt.getopt(argv, 'i:b:t:c:d:ps:o:l:f:',
                                   ['ifile=', 'broker=', 'topic=', 'client=', 'device=', 'print',
                                    'sleep=', 'offset=', 'limit=', 'filename=', 'days_offset='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)

    # initialise variables that might be set from the cmd
    coordinate_filename = BUS_FILE
    broker_address = 'localhost'
    client_name = 'random client'
    topic = 'travel_requests'
    device = uuid.getnode()
    save_filename = str(device) + ".log"
    do_print = False
    sleep = 0.01
    offset = SHIFTING_DISTANCE
    max_offset_days = DEFAULT_OFFSET_DAYS
    coord_limit = None

    # parse all command line options into variables
    for opt, arg in opts:
        if opt in ('-i', '--ifile'):
            coordinate_filename = arg
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
        elif opt in ('-l', '--limit'):
            try:
                coord_limit = int(arg)
            except ValueError:
                sys.exit("Seed limit argument [-l]/[--limit] must be an integer. Exit.")
        elif opt in ('-f', '--filename'):
            save_filename = str(arg) + ".log"
        elif opt in '--days_offset':
            max_offset_days = float(arg)

    # Create a coordinate picker using a file containing coordinates as seeds
    op_handler = OverpassHandler(coordinate_filename, coord_limit)
    coord_picker = CoordinatePicker(op_handler.get_coordinates())
    trans_type_picker = TransportationTypePicker(["tram", "ferry", "bus"], [0.2, 0.05, 0.75])
    purpose_picker = PurposePicker(p=[5, 3, 1, 1])

    # Create a RequestCreator using random selection for most fields
    travel_request_creator = RequestCreator(IdTracker(), [device], coord_picker, purpose_picker,
                                            trans_type_picker)

    # Set up topic to publish to using mqtt
    client = mqtt.Client(client_name)
    client.connect(broker_address)

    def on_disconnect(clients, userdata, rc):

        if rc != 0:
            print("Unexpected disconnection.")
            print("trying to reconnect... ")

    client.on_disconnect = on_disconnect

    # Create empty file with desired filename
    create_empty_file(save_filename)

    # Print information before starting to loop
    print('Publisher node has been started.')
    print('Publishing to client at: {}'.format(client_name))
    print('Device: \t', device)
    print('Topic: \t\t', topic)
    print('Sleeping {} seconds between messages.'.format(sleep))

    while True:
        """Loop to continuously create and publish requests."""
        req = travel_request_creator.create_random_request(offset, max_offset_days)
        save_request(req, save_filename)
        client.publish(topic, req.to_json())
        client.loop_start()

        if do_print:
            print(req.to_json())
            print(req.travelRequest['requestId'])

        time.sleep(sleep)


def resend_from_logfile():

    broker_address = 'localhost'
    client_name = 'random client'
    topic = 'travel_requests'

    print("Publisher node created.")
    print("This publisher repeats travel requests logged during a previous session.\n")

    # open a log file
    filename = fileopenbox(default="*.log", filetypes=['*.log'])  # show an "Open" dialog box and return the path to the selected file
    if filename is None or not filename.endswith(".log"):
        sys.exit("Failed to open a .log file. Exiting the program at resend#1.\nGood Bye!")

    lines = len(open(filename).readlines())
    if lines < 1:
        sys.exit("Logfile contains less than one entry. Nothing to do here.\n"
                 "Exiting the program at resend#2.\nGood Bye!")

    with open(filename) as f:
        try:
            first = int(f.readline().split("::", 1)[0])
            last = int(f.read().splitlines()[-1].split("::", 1)[0])
        except ValueError:
            sys.exit("The entries in this logfile seem to have the wrong format.\n"
                     "Exiting the program at resend#3.\nGood Bye!")

    print("Logfile opened successfully. It seems to have {0} entries.\n"
          "First one is #{1}, last one is #{2}.\n".format(lines, first, last))

    bad_inputs = True

    while bad_inputs:
        try:
            start = int(input("Enter the first entry you want to resend [{0}-{1}]: ".format(first, last)))
            stop = int(input("Enter the last entry you want to resend (inclusive) [{0}-{1}]: ".format(start, last)))
            if start < first or start > last or stop < start or stop > last:
                print("Integers not within the given boundaries.\nTry again!\n")
            else:
                bad_inputs = False
        except ValueError:
            print("Please only enter integers.")

    # Set up topic to publish to using mqtt
    client = mqtt.Client(client_name)
    client.connect(broker_address)

    def on_disconnect(clients, userdata, rc):

        if rc != 0:
            print("Unexpected disconnection.")
            print("trying to reconnect... ")

    client.on_disconnect = on_disconnect

    with open(filename) as f:
        for i, line in enumerate(f):
            if i in range(start-1, stop):
                print(line)
                line = line.replace('#*?', '\r').replace('#*!', '\n').split('::', 1)[1]  # reintroduce line breaks and split number away
                line = os.linesep.join([s for s in line.splitlines() if s])  # remove empty lines
                client.publish(topic, line)
                client.loop_start()
                time.sleep(0.1)



