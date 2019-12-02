import json
from datetime import datetime


class ComplexEncoder(json.JSONEncoder):
    """Json encoder for nested json"""

    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)


class Coordinate:
    """Defines the format for coordinates."""

    def __init__(self, latitude, longitude):
        self.coordinate = {
            'latitude': latitude,
            'longitude': longitude
        }

    def offset(self, d_latitude, d_longitude):
        self.coordinate['latitude'] += d_latitude
        self.coordinate['longitude'] += d_longitude

    def clone(self, offset_long=0, offset_lat=0):
        return Coordinate(self.coordinate['latitude'] + offset_long, self.coordinate['longitude'] + offset_lat)

    def to_tuple(self):
        """Turns Coordinates into tuples (latitude, longitutde) """
        return [self.coordinate['latitude'], self.coordinate['longitude']]

    def repr_json(self):
        """Creates a json representation of a Coordinate. Can be used recursively by """
        return dict(latitude=self.coordinate['latitude'], longitude=self.coordinate['longitude'])

    def to_json(self):
        """"""
        return json.dumps(self.coordinate)


class Device:

    def __init__(self, deviceId):
        self.deviceId = int(deviceId)

    def repr_json(self):
        return self.deviceId


class TimeStamp:

    def __init__(self, departure=datetime.now(), has_departure=True):
        self.departure = str(departure.replace(second=0, microsecond=0))
        self.has_departure = has_departure

    def repr_json(self):
        return self.departure


class Purpose:

    purposes = ['work', 'leisure', 'school', 'tourism']
    default_index = 0

    def __init__(self, index=default_index):
        self.purpose = self.purposes[index]

    def repr_json(self):
        return self.purpose


class TravelRequest:

    def __init__(self, device_id: Device, source: Coordinate, destination: Coordinate, timestamp: TimeStamp, purpose: Purpose):
        self.travelRequest = {
            'deviceId': device_id,
            'requestId': 'TODO',
            'origin': source,
            'destination': destination,
            'timeOfDeparture': timestamp,
            'purpose': purpose
        }

    def to_json(self):
        return json.dumps(self.repr_json(), cls=ComplexEncoder, indent=4)

    def repr_json(self):
        return dict(**self.travelRequest)

    def to_string(self):
        return self.travelRequest
