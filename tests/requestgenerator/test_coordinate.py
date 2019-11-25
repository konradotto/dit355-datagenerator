import unittest
from travel_request import Coordinate


class TestCoordinate(unittest.TestCase):
    def test_offset(self):
        latitude = 52.5
        longitude = 13.2
        test_coord = Coordinate(latitude, longitude)

        delta_lat = 2.1
        delta_long = -4.2
        test_coord.offset(delta_lat, delta_long)

        expected_latitude = latitude + delta_lat
        expected_longitude = longitude + delta_long

        self.assertEqual(test_coord.coordinate['latitude'], expected_latitude)
        self.assertEqual(test_coord.coordinate['longitude'], expected_longitude)


if __name__ == '__main__':
    unittest.main()
