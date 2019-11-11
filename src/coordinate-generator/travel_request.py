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
    def __init__(self, longitude, latitude):
        self.coordinate = {
            'longitude': longitude,
            'latitude': latitude
        }

    def repr_json(self):
        """Creates a json representation of a Coordinate. Can be used recursively by """
        return dict(coordinate=self.coordinate)

    def to_json(self):
        """"""
        return json.dumps(self.coordinate)


class TimeStamp:

    def __init__(self, departure=datetime.now(), arrival=datetime.now(), has_departure=True):
        self.departure = str(departure)
        self.arrival = str(arrival)
        self.has_departure = has_departure

    def repr_json(self):
        return dict(departure=self.departure, arrival=self.arrival, hasDeparture=self.has_departure)


class TravelRequest:

    def __init__(self, source: Coordinate, destination: Coordinate, timestamp: TimeStamp):
        self.travelRequest = {
            'source': source,
            'destination': destination,
            'timestamp': timestamp
        }

    def to_json(self):
        return json.dumps(self.repr_json(), cls=ComplexEncoder)

    def repr_json(self):
        return dict(travelRequest=self.travelRequest)

    def to_string(self):
        return self.travelRequest

