import math
import unittest
import geometric_operations

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


if __name__ == '__main__':
    unittest.main()
