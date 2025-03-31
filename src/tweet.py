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

from datetime import datetime
import pandas as pd
import string
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from typing import Type


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
    author_id: str
    public_metrics: Dict[str, int]
    created_at: datetime
    id: str
    conversation_id: str
    text: str
    possibly_sensitive: bool
    referenced_tweets: Optional[List[Dict[str, str]]] = None

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
            str(dictionary['author_id']),
            dictionary['public_metrics'],
            datetime.strptime(dictionary['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            str(dictionary['id']),
            str(dictionary['conversation_id']),
            dictionary['text'],
            dictionary['possibly_sensitive']
        )

        # Handle optional keys
        for key in Tweet._OPTIONAL_KEYS_TWEETS:
            if key in dictionary:
                setattr(tweet, key, dictionary[key])

        return tweet
    
    @property
    def hashtags(self) -> List[str]:
        """
        Extract hashtags from the tweet text.
        """

        # TO-DO: remove hashtag only numbers "#1"
        # TO-DO: normalize by doing everything lowercase #MahsaAmini == #mahsaamini
        hashtags = re.findall(r"#(\w+)", self.text.lower())
        return [hashtag for hashtag in hashtags if not hashtag.isdigit() and len(hashtag)>1]
    
    @property
    def mentions(self) -> List[str]:
        """
        Extract mentions from the tweet text.
        """
        return re.findall(r"@(\w+)", self.text)
    
    @property
    def urls(self) -> List[str]:
        """
        Extract URLs from the tweet text.
        """
        return re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", self.text)
    
    @property
    def is_valid(self,):
        """
        Check if a tweet is valid.

        In one of the databases (DatasetType.ISTANDWITHTRUCKERS), there are tweets that are retweets but do not start with "RT @".
        Tweet id 1486076965471849984 has the following text:
        "@xxxxx's account is temporarily unavailable because it violates the Twitter Media Policy. Learn more."
        Real handle of author @xxxxx is hidden for privacy reasons.

        """
        is_retweet =  hasattr(self, 'referenced_tweets') and \
            self.referenced_tweets is not None and any(
                tweet['type'] == 'retweeted' for tweet in self.referenced_tweets
            )
        if is_retweet and not self.text.startswith("RT @"):
            return False
        return True

    @property
    def is_retweet(self,):
        """
        Check if a tweet is a retweet.
        """
        is_retweet =  hasattr(self, 'referenced_tweets') and \
            self.referenced_tweets is not None and any(
                tweet['type'] == 'retweeted' for tweet in self.referenced_tweets
            )
        if is_retweet and not self.text.startswith("RT @"):
            raise ValueError(f"The tweet is a retweet but the text does not match the expected pattern. id: {self.id}")
        return is_retweet

    @property
    def is_reply(self, ) -> bool:
        """
        Check if a tweet is a reply.
        """
        is_reply =  hasattr(self, 'referenced_tweets') and \
            self.referenced_tweets is not None and any(
                tweet['type'] == 'replied_to' for tweet in self.referenced_tweets
            )
        return is_reply

    @property
    def sanitized_text(self,):
        """
        Return the tweet text without hashtags, mentions, URLs, and punctuation.
        """
        text = self.text.lstrip('RT ')  # Remove 'RT ' if it exists
        
        # Remove hashtags, mentions, and URLs efficiently
        for item in self.hashtags + self.mentions:
            text = text.replace(f'#{item}', '').replace(f'@{item}', '')
        for url in self.urls:
            text = text.replace(url, '')

        # Remove punctuation efficiently using str.translate
        text = text.translate(str.maketrans('', '', string.punctuation)).strip()
        
        return text

    def __str__(self):
        """
        Return a string representation of the Tweet object showing only author_id, id, and text.
        """
        return f"Tweet(author_id={self.author_id}, id={self.id}, text={self.text}, date={self.created_at})"

    def __repr__(self):
        """
        Return a formal string representation of the Tweet object showing only author_id, id, and text.
        """
        return f"Tweet(author_id={self.author_id}, id={self.id}, text={self.text}, date={self.created_at})"

    @staticmethod
    def _parse_referenced_tweets(row):
        """
        Parse the referenced tweets from a row in the XLSX file.
        """
        if pd.notna(row['referenced_tweet_id']) and pd.notna(row['referenced_tweet_type']):
            return [{'type': row['referenced_tweet_type'], 'id': str(row['referenced_tweet_id'])}]
        return None

    @staticmethod
    def transform_xlsx_to_tweets(xlsx_filepath: str) -> List["Tweet"]:
        """
        Transform an XLSX file containing tweet data into a list of Tweet objects.
        """
        tweets = []
        df = pd.read_excel(xlsx_filepath)
        
        for _, row in df.iterrows():
            tweet = Tweet(
                lang=row['language'],
                author_id=str(row['userid']),
                public_metrics={
                    'retweet_count': int(row['retweet_count']),
                    'reply_count': int(row['reply_count']),
                    'like_count': int(row['like_count']),
                    'quote_count': int(row['quote_count']),
                    'bookmark_count': 0,  # Not available in XLSX, set to 0
                    'impression_count': 0  # Not available in XLSX, set to 0
                },
                created_at=datetime.strptime(row['date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                id=str(row['tweet_id']),
                conversation_id=str(row['tweet_id']) if pd.isna(row['in_reply_to_tweet_id']) else int(row['in_reply_to_tweet_id']),
                text=row['text'],
                possibly_sensitive=str(row['possibly_sensitive']).lower() == 'true',
                referenced_tweets=Tweet._parse_referenced_tweets(row)
            )
            tweets.append(tweet)
        
        return tweets