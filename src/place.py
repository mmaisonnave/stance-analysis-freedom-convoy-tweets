"""
Module: place.py

This module defines the `Place` class, which represents a geographical location with attributes 
such as name, country, coordinates, and type.

The class is implemented using Python's `dataclass` to streamline object creation and representation.

Features:
- `Place`: A dataclass representing a geographical place with essential attributes.
- `from_dict(dictionary: dict) -> Place`: Creates a `Place` instance from a dictionary.
- `is_valid_place_dictionary(dictionary: dict) -> bool`: Validates whether a dictionary contains the required keys to instantiate a `Place`.
- `__str__() -> str`: Returns a human-readable string representation of the place.
- `__repr__() -> str`: Returns a detailed string representation of the place, useful for debugging.

Constants:
- `_KEYS_COMMON_TO_ALL_PLACES`: A set of required keys that every `Place` dictionary must contain.
- `_OPTIONAL_KEYS_PLACES`: A set of optional keys that may be included in a `Place` dictionary (currently empty).

Usage:
    place_data = {
        "country_code": "US",
        "geo": {"type": "Point", "coordinates": [-74.006, 40.7128]},
        "name": "New York",
        "country": "United States",
        "full_name": "New York, NY",
        "id": "12345",
        "place_type": "city"
    }

    place = Place.from_dict(place_data)
    print(place)  # Output: Place(id=12345, full_name=New York, NY, country_code=US)

This module ensures consistency when handling geographical location data and provides validation for place dictionaries.
"""



from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Place:
    """
    Class to handle the object "Place"
    """    
    _KEYS_COMMON_TO_ALL_PLACES = {
        'country_code', 
        'geo', 
        'name', 
        'country', 
        'full_name', 
        'id', 
        'place_type'
        }

    _OPTIONAL_KEYS_PLACES = {}

    country_code: str
    geo: Dict
    name: str
    country: str
    full_name: str
    id: str
    place_type: str

    @staticmethod
    def from_dict(dictionary: dict) -> "Place":
        """
        Create a Place object from a dictionary.
        """
        if Place.is_valid_place_dictionary(dictionary):
            return Place(
                country_code=dictionary['country_code'],
                geo=dictionary['geo'],
                name=dictionary['name'],
                country=dictionary['country'],
                full_name=dictionary['full_name'],
                id=dictionary['id'],
                place_type=dictionary['place_type']
            )
        else:
            raise ValueError("Invalid dictionary: Missing required keys")

    @staticmethod
    def is_valid_place_dictionary(dictionary: dict):
        """
        Check if a given dictionary has all required properties to be a Place. 
        """
        return Place._KEYS_COMMON_TO_ALL_PLACES.issubset(dictionary.keys())

    def __str__(self):
        """
        Return a user-friendly string representation with only id, full_name, and country_code.
        """
        return f"Place(id={self.id}, full_name={self.full_name}, country_code={self.country_code})"

    def __repr__(self):
        """
        Return a more formal string representation for debugging with only id, full_name, and country_code.
        """
        return f"Place(id='{self.id}', full_name='{self.full_name}', country_code='{self.country_code}')"
