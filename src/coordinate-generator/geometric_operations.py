from travel_request import Coordinate
import geopy.distance as dist
import warnings
import math


def calc_distance(source: Coordinate, target: Coordinate):
    return dist.geodesic(source.to_tuple(), target.to_tuple())


def shift_coordinate(coord_before: Coordinate, angle_rad, distance):
    """Shift a coordinate by a given distance in a given direction."""

    # do nothing if the distance doesn't make sense
    if distance <= 0:
        warnings.warn("Can't shift by distance <= 0. Returns the original Coordinate.")
        return coord_before

    if angle_rad <= 0:
        warnings.warn("Please provide a positive angle (ideally between 0 and 2pi).")
        return coord_before


def transform_angular_distance_to_cartesic(angle_rad, distance):
    """Function to transform a nautical angular distance to its Cartesian form.

    Beware that nautical distances are defined clockwise starting at North."""

    # Divide distance into longitudinal (dist_x) and latitudinal (dist_y) parts using trigonometric relations.
    dist_x = math.asin(angle_rad) * distance
    dist_y = math.acos(angle_rad) * distance

    return dist_x, dist_y
