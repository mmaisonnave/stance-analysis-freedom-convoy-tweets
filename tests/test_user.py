import unittest
import sys
sys.path.append("..")
from src.user import User

class TestUser(unittest.TestCase):
    def setUp(self):
        self.valid_user_data = {
            "protected": False,
            "username": "john_doe",
            "created_at": "2023-01-01T12:00:00Z",
            "name": "John Doe",
            "description": "Software Engineer",
            "verified": True,
            "profile_image_url": "https://example.com/johndoe.jpg",
            "id": "123456789",
            "public_metrics": {"followers_count": 100, "following_count": 50},
            "url": "https://example.com",
            "location": "New York, USA",
            "entities": {},
        }

    def test_from_dict_valid_data(self):
        user = User.from_dict(self.valid_user_data)
        self.assertEqual(user.username, "john_doe")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.id, "123456789")
        self.assertEqual(user.verified, True)
        self.assertEqual(user.profile_image_url, "https://example.com/johndoe.jpg")
        self.assertEqual(user.public_metrics["followers_count"], 100)
        self.assertEqual(user.url, "https://example.com")
        self.assertEqual(user.location, "New York, USA")

    def test_from_dict_missing_required_keys(self):
        invalid_data = {"username": "john_doe"}  # Missing required keys
        with self.assertRaises(ValueError):
            User.from_dict(invalid_data)

    def test_is_valid_user_dictionary(self):
        self.assertTrue(User.is_valid_user_dictionary(self.valid_user_data))
        invalid_data = {"username": "john_doe"}
        self.assertFalse(User.is_valid_user_dictionary(invalid_data))

    def test_str_representation(self):
        user = User.from_dict(self.valid_user_data)
        expected_str = "User(username=john_doe, name=John Doe, id=123456789)"
        self.assertEqual(str(user), expected_str)

    def test_repr_representation(self):
        user = User.from_dict(self.valid_user_data)
        expected_repr = "User(username='john_doe', name='John Doe', id='123456789')"
        self.assertEqual(repr(user), expected_repr)

if __name__ == "__main__":
    unittest.main()