import math
import unittest
import geometric_operations
from travel_request import Coordinate
from parameterized import parameterized


class TestGeometricOperations(unittest.TestCase):
    """Unit tests to determine the proper implementation of geometric operations."""

    @parameterized.expand([
        ["north", 0, 5.5, 0, 5.5],
        ["east", math.pi/2, 7.3, 7.3, 0],
        ["south", math.pi, 12, 0, -12],
        ["west", 3/2 * math.pi, 204.12, -204.12, 0],
    ])
    def test_transform_angular_distance_to_cartesian(self, name, angle, dist, expected_x, expected_y):
        dist_x, dist_y = geometric_operations.transform_angular_distance_to_cartesian(angle, dist)
        self.assertAlmostEqual(dist_x, expected_x, msg="Expected x-value and actual x-value should be identical",
                               delta=1e-10)
        self.assertAlmostEqual(dist_y, expected_y, msg="Expected y-value and actual y-value should be identical",
                               delta=1e-10)

    @parameterized.expand([
        ["gbg", Coordinate(11, 52), 500, 0.001, 1e-1]
    ])
    def test_approximate_longitude(self, name, location, desired_x_dist, precision=0.001, delta=5e-1):

        longitude_offset, error = geometric_operations.approximate_longitude(desired_x_dist, location)
        self.assertLessEqual(error, precision, f"Error should be less than {precision}")

        actual_x_dist = geometric_operations.calc_distance(location, location.clone(offset_long=longitude_offset)).m
        self.assertAlmostEqual(desired_x_dist, actual_x_dist,
                               msg="The actual distance and calculated distance should be about the same", delta=delta)


if __name__ == '__main__':
    unittest.main()
