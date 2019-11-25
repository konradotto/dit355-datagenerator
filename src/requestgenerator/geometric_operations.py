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

    dist_x, dist_y = transform_angular_distance_to_cartesian(angle_rad, distance)

    longitude_offset = approximate_longitude(dist_x, coord_before)
    latitude_offset = approximate_latitude(dist_y, coord_before)
    
    return Coordinate.clone(offset_lat=latitude_offset, offset_long=longitude_offset)


def transform_angular_distance_to_cartesian(angle_rad, distance):
    """Function to transform a nautical angular distance to its Cartesian form.

    Beware that nautical distances are defined clockwise starting at North."""

    # Divide distance into longitudinal (dist_x) and latitudinal (dist_y) parts using trigonometric relations.
    dist_x = math.sin(angle_rad) * distance
    dist_y = math.cos(angle_rad) * distance

    return dist_x, dist_y


def approximate_longitude(desired_x_distance, location, longitude_scale_offset=0.1):
    """Function to approximate the offset in degrees of longitude needed to get the desired x-distance."""

    scale_distance = calc_distance(location, location.clone(offset_long=longitude_scale_offset))

    # If scale distance is way bigger than desired distance, try again with new scale offset
    if scale_distance/10.0 > desired_x_distance:
        return approximate_longitude(desired_x_distance, location, longitude_scale_offset / 10.0)

    # If scale distance is way smaller than desired distance, try again with new scale offset
    if scale_distance * 20.0 < desired_x_distance:
        return approximate_longitude(desired_x_distance, location, longitude_scale_offset * 10.0)

    longitude_offset = longitude_scale_offset * (desired_x_distance / scale_distance)

    # Calculate relative error of the approximation
    approximation_error = math.fabs(calc_distance(location, location.clone(offset_long=longitude_offset)) - desired_x_distance) / desired_x_distance

    return longitude_offset, approximation_error


def approximate_latitude(desired_distance, location):
    """Function to approximate the offset in degrees of latitude needed to get the desired x-distance."""

    # TODO: Calculations to turn desired metrical offset into degrees at location
    return desired_distance