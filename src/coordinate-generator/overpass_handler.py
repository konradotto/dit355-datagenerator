"""
Script to handle data files produced with overpass.
"""
import json
from src.utils import path_utils
import random
from travel_request import TravelRequest, TimeStamp, Coordinate
import paho.mqtt.client as mqtt #import the client1
import time
from operator import itemgetter
from datetime import datetime

BUS_FILE = path_utils.get_data_path().joinpath('bus_stops_gothenburg.geojson')


def load_geo_features(filename):
    """Opens a json-file containing a list of geo features and returns them as object."""
    with open(filename) as f:
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

    def pick(self):
        coord = random.choice(self.coordinates)
        return Coordinate(coord[0], coord[1])


class RequestCreator:

    def __init__(self, picker: CoordinatePicker):
        self.picker = picker

    def create_timed_request(self, timestamp):
        source = self.picker.pick()
        target = self.picker.pick()
        return TravelRequest(source, target, timestamp)


if __name__ == "__main__":

    op_handler = OverpassHandler(BUS_FILE)
    bus_stop_coordinates = op_handler.get_coordinates()

    print(max(bus_stop_coordinates, key=itemgetter(0))[0], min(bus_stop_coordinates, key=itemgetter(0))[0])
    print(max(bus_stop_coordinates, key=itemgetter(1))[1], min(bus_stop_coordinates, key=itemgetter(1))[1])


    picker = CoordinatePicker(op_handler.get_coordinates())
    print(picker.pick())

    client = mqtt.Client('random client')

    brooker_address = '192.168.43.61'
    client.connect(brooker_address)

    topic = "hello/world"

    while True:
        timestamp = TimeStamp(datetime.now(), datetime.now(), True)
        req = TravelRequest(picker.pick(), picker.pick(), timestamp)
        client.publish(topic, req.to_json())
        print(req.to_json())
        time.sleep(1)


