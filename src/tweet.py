"""
tweet.py

This module defines a Tweet class to represent and validate Twitter tweet data. 
It provides methods for constructing a Tweet object from a dictionary, 
validating tweet data, and generating string representations.

Classes:
    - Tweet: A dataclass representing a Tweet, with attributes such as author_id, 
      created_at, text, and public metrics.

Methods:
    - is_valid_tweet_dictionary(dictionary: dict) -> bool:
        Checks if a dictionary contains the required keys to be a valid Tweet.

    - from_dict(dictionary: dict) -> Tweet:
        Constructs a Tweet object from a dictionary.

Attributes:
    - _KEYS_COMMON_TO_ALL_TWEETS (set): Required keys for a Tweet dictionary.
    - _OPTIONAL_KEYS_TWEETS (set): Optional keys that may be present in a Tweet dictionary.

"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Tweet:
    """
    Class to handle the object "Tweet"
    """
    _KEYS_COMMON_TO_ALL_TWEETS = {
        'author_id',
        'conversation_id',
        'created_at',
        'edit_history_tweet_ids',
        'entities',
        'id',
        'lang',
        'possibly_sensitive',
        'public_metrics',
        'text'
    }
    _OPTIONAL_KEYS_TWEETS = {
        'attachments',
        'context_annotations',
        'geo',
        'in_reply_to_user_id',
        'referenced_tweets'
    }

    lang: str
    author_id: int
    public_metrics: Dict[str, int]
    created_at: str
    id: int
    conversation_id: int
    text: str
    possibly_sensitive: bool

    @staticmethod
    def is_valid_tweet_dictionary(dictionary: dict):
        """
        Check if a given dictionary has all required properties to be a Tweet. 
        """
        return Tweet._KEYS_COMMON_TO_ALL_TWEETS.issubset(dictionary.keys())

    @staticmethod
    def from_dict(dictionary: dict):
        """
        Build a Tweet object from a given dictionary.
        """
        if not Tweet.is_valid_tweet_dictionary(dictionary):
            raise ValueError("The dictionary does not contain all required keys for a valid Tweet.")

        tweet = Tweet(
            dictionary['lang'],
            dictionary['author_id'],
            dictionary['public_metrics'],
            dictionary['created_at'],
            dictionary['id'],
            dictionary['conversation_id'],
            dictionary['text'],
            dictionary['possibly_sensitive']
        )

        # Handle optional keys
        for key in Tweet._OPTIONAL_KEYS_TWEETS:
            if key in dictionary:
                setattr(tweet, key, dictionary[key])

        return tweet
    

    def __str__(self):
        """
        Return a string representation of the Tweet object showing only author_id, id, and text.
        """
        return f"Tweet(author_id={self.author_id}, id={self.id}, text={self.text})"

    def __repr__(self):
        """
        Return a formal string representation of the Tweet object showing only author_id, id, and text.
        """
        return f"Tweet(author_id={self.author_id}, id={self.id}, text={repr(self.text)})"
