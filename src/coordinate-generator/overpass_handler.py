"""
Script to handle data files produced with overpass.
"""
import json
from src.utils import path_utils

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


def load_coordinate_list(filename=BUS_FILE):
    """Directly extract the coordinates of features from a json-file."""
    return extract_coordinate_list(load_geo_features(filename))


if __name__ == "__main__":
    bus_stop_coordinates = load_coordinate_list()
    for coordinate in bus_stop_coordinates:
        print(coordinate)
    print(len(bus_stop_coordinates))
