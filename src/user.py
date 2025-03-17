"""
Module: user.py

This module defines the `User` class, which represents a user with various attributes, 
such as username, name, account creation date, verification status, and profile-related details.

The class is implemented using Python's `dataclass` to simplify initialization and representation.

Features:
- `User`: A dataclass representing a user with required and optional attributes.
- `from_dict(dictionary: dict) -> User`: Creates a `User` instance from a dictionary.
- `is_valid_user_dictionary(dictionary: dict) -> bool`: Checks whether a dictionary contains the required keys to instantiate a `User`.
- `__str__() -> str`: Returns a human-readable string representation of the user.
- `__repr__() -> str`: Returns a detailed string representation of the user, useful for debugging.

Constants:
- `_KEYS_COMMON_TO_ALL_USERS`: A set of required keys that every `User` dictionary must contain.
- `_OPTIONAL_KEYS_USERS`: A set of optional keys that may be included in a `User` dictionary.

Usage:
    user_data = {
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
        "location": "New York, USA"
    }

    user = User.from_dict(user_data)
    print(user)  # Output: User(username=john_doe, name=John Doe, id=123456789)

This module ensures consistency when handling user data and provides validation for user dictionaries.
"""


from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class User:
    """
    Class to handle the object "User"
    """
    _KEYS_COMMON_TO_ALL_USERS = {
        'protected', 
        'username', 
        'created_at', 
        'name', 
        'description', 
        'verified', 
        'profile_image_url', 
        'id',
        'public_metrics'
        }

    _OPTIONAL_KEYS_USERS = {
        'withheld',
        'url',
        'entities', 
        'pinned_tweet_id',
        'location'
        }

    protected: bool
    username: str
    created_at: str
    name: str
    description: str
    entities: Dict
    verified: bool
    profile_image_url: str
    id: str
    public_metrics: Dict
    withheld: Optional[Dict] = None
    url: Optional[str] = None
    pinned_tweet_id: Optional[str] = None
    location: Optional[str] = None

    @staticmethod
    def from_dict(dictionary: dict) -> "User":
        """
        Create a User object from a dictionary.
        """
        if User.is_valid_user_dictionary(dictionary):
            return User(
                protected=dictionary['protected'],
                username=dictionary['username'],
                created_at=dictionary['created_at'],
                name=dictionary['name'],
                description=dictionary['description'],
                verified=dictionary['verified'],
                profile_image_url=dictionary['profile_image_url'],
                id=dictionary['id'],
                public_metrics=dictionary['public_metrics'],
                withheld=dictionary.get('withheld'),
                url=dictionary.get('url'),
                entities=dictionary.get('entities'),
                pinned_tweet_id=dictionary.get('pinned_tweet_id'),
                location=dictionary.get('location')
            )
        else:
            raise ValueError("Invalid dictionary: Missing required keys")

    @staticmethod
    def is_valid_user_dictionary(dictionary: dict):
        """
        Check if a given dictionary has all required properties to be a User. 
        """
        return User._KEYS_COMMON_TO_ALL_USERS.issubset(dictionary.keys())

    def __str__(self) -> str:
        """
        Return a string representation of the User with username, name, and id.
        """
        return f"User(username={self.username}, name={self.name}, id={self.id})"

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the User with username, name, and id.
        """
        return f"User(username={self.username!r}, name={self.name!r}, id={self.id!r})"
