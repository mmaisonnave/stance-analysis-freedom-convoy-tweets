import sys
sys.path.append('..')
from datetime import datetime
from src import io
from src.convoy_protest_dataset import DatasetType
from src.convoy_protest_dataset import ConvoyProtestDataset
from src.tweet import Tweet
from collections import Counter
from core.llms import OpenAIStanceDetector

def main():
    # ========== Retrieve all tweets: ========== 
    users, tweets, places = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL, removed_repeated=True)
    io.info(f'Len unique tweets:                         {len(tweets):,}')

    # ========== Filter by date: ========== 
    start = datetime(2022, 1, 1)
    end = datetime(2022, 3, 31)
    tweets = Tweet.filter_tweets_by_date(tweets, start=start, end=end)
    io.info(f'Len unique tweets in range:                {len(tweets):,}')


    # ========== Remove retweets: ========== 
    tweets = [tweet for tweet in tweets if not tweet.is_retweet]
    io.info(f'Tweet count with retweets removed:         {len(tweets):,}')

    # ========== Remove tweets with URL: ========== 
    tweets = [tweet for tweet in tweets if len(tweet.urls)==0]
    io.info(f'Tweet count with tweets with urls removed: {len(tweets):,}')


    detector = OpenAIStanceDetector()


    author_ids = [author_id for author_id, count in 
                  Counter([tweet.author_id for tweet in tweets ]).items() 
                  if count>=detector.max_tweet_count]

    io.info(f'Number of users with more than {detector.max_tweet_count} tweets = {len(author_ids)}.')




if __name__ == '__main__':
    main()