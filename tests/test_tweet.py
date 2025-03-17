import unittest
import sys
sys.path.append('..')
from src.tweet import Tweet

class TestTweet(unittest.TestCase):
    
    def setUp(self):
        """Set up a valid tweet dictionary for testing."""
        self.valid_tweet_dict = {
            'author_id': 123456,
            'conversation_id': 78910,
            'created_at': '2025-03-14T12:34:56Z',
            'edit_history_tweet_ids': ['111', '222'],
            'entities': {},
            'id': 654321,
            'lang': 'en',
            'possibly_sensitive': False,
            'public_metrics': {'retweet_count': 10, 'like_count': 100},
            'text': 'This is a test tweet.'
        }
        
    def test_is_valid_tweet_dictionary_valid(self):
        """Test that a valid tweet dictionary is recognized as valid."""
        self.assertTrue(Tweet.is_valid_tweet_dictionary(self.valid_tweet_dict))
        
    def test_is_valid_tweet_dictionary_missing_keys(self):
        """Test that a dictionary missing required keys is recognized as invalid."""
        invalid_tweet_dict = self.valid_tweet_dict.copy()
        del invalid_tweet_dict['author_id']
        self.assertFalse(Tweet.is_valid_tweet_dictionary(invalid_tweet_dict))
        
    def test_from_dict_valid(self):
        """Test that a valid tweet dictionary is correctly converted into a Tweet object."""
        tweet = Tweet.from_dict(self.valid_tweet_dict)
        self.assertEqual(tweet.author_id, 123456)
        self.assertEqual(tweet.id, 654321)
        self.assertEqual(tweet.text, 'This is a test tweet.')
        self.assertEqual(tweet.public_metrics['retweet_count'], 10)
        
    def test_from_dict_missing_keys(self):
        """Test that from_dict raises an error when required keys are missing."""
        invalid_tweet_dict = self.valid_tweet_dict.copy()
        del invalid_tweet_dict['text']
        with self.assertRaises(ValueError):
            Tweet.from_dict(invalid_tweet_dict)
        
    def test_tweet_str(self):
        """Test the string representation of a Tweet object."""
        tweet = Tweet.from_dict(self.valid_tweet_dict)
        expected_str = "Tweet(author_id=123456, id=654321, text=This is a test tweet.)"
        self.assertEqual(str(tweet), expected_str)
        
    def test_tweet_repr(self):
        """Test the repr representation of a Tweet object."""
        tweet = Tweet.from_dict(self.valid_tweet_dict)
        expected_repr = "Tweet(author_id=123456, id=654321, text='This is a test tweet.')"
        self.assertEqual(repr(tweet), expected_repr)
        
if __name__ == "__main__":
    unittest.main()
