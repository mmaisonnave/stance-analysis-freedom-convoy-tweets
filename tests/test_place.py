import unittest
import sys
sys.path.append('..')
from src.place import Place

class TestPlace(unittest.TestCase):
    def setUp(self):
        """Set up a sample valid place dictionary for tests."""
        self.valid_place_dict = {
            "country_code": "US",
            "geo": {"type": "Point", "coordinates": [-74.006, 40.7128]},
            "name": "New York",
            "country": "United States",
            "full_name": "New York, NY",
            "id": "12345",
            "place_type": "city"
        }

    def test_is_valid_place_dictionary_valid(self):
        """Test that a valid place dictionary is recognized as valid."""
        self.assertTrue(Place.is_valid_place_dictionary(self.valid_place_dict))

    def test_is_valid_place_dictionary_invalid(self):
        """Test that an invalid place dictionary is recognized as invalid."""
        invalid_dict = {"country_code": "US", "name": "New York"}  # Missing required keys
        self.assertFalse(Place.is_valid_place_dictionary(invalid_dict))

    def test_from_dict_valid(self):
        """Test that a Place instance is correctly created from a valid dictionary."""
        place = Place.from_dict(self.valid_place_dict)
        self.assertIsInstance(place, Place)
        self.assertEqual(place.id, "12345")
        self.assertEqual(place.name, "New York")
        self.assertEqual(place.country_code, "US")
        self.assertEqual(place.geo, {"type": "Point", "coordinates": [-74.006, 40.7128]})

    def test_from_dict_invalid(self):
        """Test that an invalid dictionary raises a ValueError."""
        invalid_dict = {"country_code": "US", "name": "New York"}  # Missing required keys
        with self.assertRaises(ValueError):
            Place.from_dict(invalid_dict)

    def test_str_representation(self):
        """Test the __str__ method."""
        place = Place.from_dict(self.valid_place_dict)
        expected_str = "Place(id=12345, full_name=New York, NY, country_code=US)"
        self.assertEqual(str(place), expected_str)

    def test_repr_representation(self):
        """Test the __repr__ method."""
        place = Place.from_dict(self.valid_place_dict)
        expected_repr = "Place(id='12345', full_name='New York, NY', country_code='US')"
        self.assertEqual(repr(place), expected_repr)

if __name__ == "__main__":
    unittest.main()
