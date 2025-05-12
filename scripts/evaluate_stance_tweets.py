import numpy as np
import argparse

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
from core.llms import OpenAIStanceDetector



def clean():
    # Add your logic to remove files here
    io.info("Cleaning up files...")
    config = PathsHandler()
    output_file = config.get_path('tweet-evaluation-output')
    os.remove(output_file)


def run_main():
    SEED = 172027145
    config = PathsHandler()

    output_file = config.get_path('tweet-evaluation-output')
    io.info(f'Script will store results in {output_file}')


    # ========== Retrieve all tweets: ==========
    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL, removed_repeated=True)
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


    char_count = sum([len(tweet.sanitized_text) for tweet in tweets])
    io.info(f'char_count={char_count} (to process with LLM)')


    detector = OpenAIStanceDetector()

    results = []

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as file:
            results = json.load(file)

    already_proccessed_tweet_ids = {result_item['tweet_id'] for result_item in results}
    io.info(f'already processed elements:  {len(already_proccessed_tweet_ids)}')


    tweets = [tweet for tweet in tweets if tweet.id not in already_proccessed_tweet_ids]
    io.info(f'Elements left to process:    {len(tweets)}')


    rng = np.random.default_rng(seed=SEED)

    rng.shuffle(tweets)

    for tweet in tweets[:20000]:
        result = detector.evaluate_tweet(tweet)
        results.append(result)

    
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    io.info('Results saved to disk.')


def main():
    io.info('Starting script evaluate_stance_users.py ...')
    parser = argparse.ArgumentParser(description="A script with a --clean option.")
    parser.add_argument("--clean", action="store_true", help="Clean up files instead of running main logic.")
    args = parser.parse_args()

    if args.clean:
        clean()
    else:
        run_main()
    
    io.info('Finishing script evaluate_stance_users.py ...')


if __name__ == '__main__':
    main()