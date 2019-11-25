import unittest
from travel_request import Coordinate


class TestCoordinate(unittest.TestCase):
    def test_offset(self):
        longitude = 13.2
        latitude = 52.5
        test_coord = Coordinate(longitude, latitude)

        delta_long = -4.2
        delta_lat = 2.1
        test_coord.offset(delta_long, delta_lat)

        expected_longitude = longitude + delta_long
        expected_latitude = latitude + delta_lat

        self.assertEqual(test_coord.coordinate['longitude'], expected_longitude)
        self.assertEqual(test_coord.coordinate['latitude'], expected_latitude)


if __name__ == '__main__':
    unittest.main()
