"""
Script to handle data files produced with overpass.
"""
import uuid
import calendar
import json
from src.utils import path_utils
import random
from src.requestgenerator.travel_request import TravelRequest, Issuance,TimeStamp, Coordinate, Device, Purpose
from src.requestgenerator.geometric_operations import shift_coordinate
import paho.mqtt.client as mqtt  # import the client
import time
import math
from datetime import datetime

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
        self.current_id = 0

    def next(self):
        result = self.current_id
        self.current_id = self.current_id + 1
        return result


class PurposePicker:

    def __init__(self, purposes=['work', 'leisure', 'school', 'tourism']):
        self.purposes = purposes

    def pick_random(self):
        return Purpose(random.choice(self.purposes))


class DevicePicker:

    def __init__(self, devices):
        self.devices = devices

    def pick_random(self):
        return Device(random.choice(self.devices))


class TransportationTypePicker:

    def __init__(self, types):
        self.transportation_types = types

    def pick_random(self):
        return random.choice(self.transportation_types)


class RequestCreator:

    def __init__(self, id_tracker: IdTracker, devices, coordinate_picker: CoordinatePicker,
                 purpose_picker: PurposePicker, type_picker: TransportationTypePicker):
        self.id_tracker = id_tracker
        self.device_picker = DevicePicker(devices)
        self.coordinate_picker = coordinate_picker
        self.purpose_picker = purpose_picker
        self.transportation_type_picker = type_picker

    def create_random_request(self):
        device_id = self.device_picker.pick_random()
        request_id = self.id_tracker.next()
        request_issuance = calendar.timegm(time.gmtime())
        request_source = self.coordinate_picker.pick_randomly_with_circular_uncertainty()
        request_target = self.coordinate_picker.pick_randomly_with_circular_uncertainty()
        request_timestamp = TimeStamp(datetime.now(), True)
        request_purpose = self.purpose_picker.pick_random()
        transportation_type = self.transportation_type_picker.pick_random()
        return TravelRequest(device_id, request_id, request_issuance,request_source, request_target, request_timestamp, request_purpose,
                             transportation_type)

    def create_timed_request(self, timestamp):
        source = self.picker.pick()
        target = self.picker.pick()
        return TravelRequest(source, target, timestamp)

    def create_issuance_request(self, issuance):
        source = self.picker.pick()
        target = self.picker.pick()
        return TravelRequest(source, target, issuance)

def run():
    # Create a coordinate picker for Gothenburg based on the location of bus stops in the city
    op_handler = OverpassHandler(BUS_FILE)
    bus_stop_coordinates = op_handler.get_coordinates()
    coord_picker = CoordinatePicker(op_handler.get_coordinates())
    trans_type_picker = TransportationTypePicker(["tram", "ferry", "bus"])

    # Create a RequestCreator using random selection for most fields
    travel_request_creator = RequestCreator(IdTracker(), [uuid.getnode()], coord_picker, PurposePicker(),
                                            trans_type_picker)

    # Set up topic to publish to using mqtt
    client = mqtt.Client('random client')
    broker_address = 'localhost'
    client.connect(broker_address)
    topic = "travel_requests"

    while True:
        """Loop to continuously create and publish requests."""
        req = travel_request_creator.create_random_request()
        client.publish(topic, req.to_json())

        print(req.to_json())
        print(req.travelRequest['requestId'])
        time.sleep(0.01)
