from .travel_request import Coordinate
import geopy.distance as dist


def calc_distance(source: Coordinate, target: Coordinate):
    return dist.geodesic(source.to_tuple(), target.to_tuple())


