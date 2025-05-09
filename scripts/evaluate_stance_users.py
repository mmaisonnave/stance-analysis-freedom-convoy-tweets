import json
import os
import sys
sys.path.append('..')
from datetime import datetime
from src import io
from src.convoy_protest_dataset import DatasetType
from src.convoy_protest_dataset import ConvoyProtestDataset
from src.paths_handler import PathsHandler
from src.tweet import Tweet
from collections import Counter
from core.llms import OpenAIStanceDetector

def main():
    io.info('Starting script evaluate_stance_users.py ...')
    config = PathsHandler()

    OUTPUT_FILE = config.get_path('user-evaluation-output')
    io.info(f'Script will store results in {OUTPUT_FILE}')


    # ========== Retrieve all tweets: ========== 
    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.MENTIONERS, removed_repeated=True)
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


    author_ids = {author_id for author_id, count in
                  Counter([tweet.author_id for tweet in tweets ]).items() 
                  if count>=detector.max_tweet_count}

    io.info(f'Number of users with more than {detector.max_tweet_count} tweets = {len(author_ids)}.')

    results = []

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as file:
            results = json.load(file)

    already_proccessed_ids = {result_item['author_id'] for result_item in results}
    
    io.info(f'elements to process:         {len(author_ids)}')
    io.info(f'already processed elements:  {len(already_proccessed_ids)}')
    author_ids = author_ids.difference(already_proccessed_ids)
    io.info(f'Elements left to process:    {len(author_ids)}')

    for author_id in author_ids:
        tweets_from_user = [tweet for tweet in tweets if tweet.author_id==author_id]
        result = detector.evaluate_user(tweets_from_user)
        result['author_id'] = author_id
        results.append(result)

    
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    io.info('Finishing script evaluate_stance_users.py ...')



if __name__ == '__main__':
    main()