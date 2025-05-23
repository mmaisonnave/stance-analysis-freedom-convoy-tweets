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



def clean(output_file: str):
    # Ask for confirmation before removing the file
    confirmation = input(f"Are you sure you want to delete '{output_file}'? [y/N]: ").strip().lower()
    if confirmation == 'y':
        io.info("Cleaning up files...")
        os.remove(output_file)
        io.info(f"'{output_file}' has been deleted.")
    else:
        io.info("Cleanup aborted by user.")



def run_main(output_file: str):
    BATCH_SIZE = 200
    SAMPLE_SIZE= 1000

    SEED = 172027145
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


    detector = OpenAIStanceDetector()

    results = []

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as file:
            results = json.load(file)

    already_processed_tweet_ids = {result_item['tweet_id'] for result_item in results}
    io.info(f'already processed elements:  {len(already_processed_tweet_ids)}')


    tweets = [tweet for tweet in tweets if tweet.id not in already_processed_tweet_ids]
    io.info(f'Elements left to process:    {len(tweets)}')


    rng = np.random.default_rng(seed=SEED)

    rng.shuffle(tweets)


    SAMPLE_SIZE=min(SAMPLE_SIZE, len(tweets))
    for i in range(0, SAMPLE_SIZE, BATCH_SIZE):
        batch = tweets[i:min(i+BATCH_SIZE, SAMPLE_SIZE)]
        io.info(f'len(batch)={len(batch)}       ({i} - {min(i+BATCH_SIZE, SAMPLE_SIZE)})')
        for tweet in batch:
            result = detector.evaluate_tweet(tweet)
            results.append(result)

        # Save results after each batch
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=4)

    io.info('Results saved to disk.')

def count(output_file: str) -> None:
    count_no = 0
    neutral_count = 0
    right_count = 0
    left_count = 0
    if os.path.exists(output_file):

        with open(output_file, 'r', encoding='utf-8') as file:
            results = json.load(file)
        count_no = len(results)
        right_count = len([result for result in results if result['llm_response'] == 'right'])
        neutral_count = len([result for result in results if result['llm_response'] == 'neutral'])
        left_count = len([result for result in results if result['llm_response'] == 'left'])
    io.info(f'No of results found: {count_no}')
    io.info(f'No of left found:    {left_count}')
    io.info(f'No of neutral found: {neutral_count}')
    io.info(f'No of right found:   {right_count}')

def main():
    config = PathsHandler()
    output_file = config.get_path('tweet-evaluation-output')
    io.info('Starting script evaluate_stance_users.py ...')
    parser = argparse.ArgumentParser(description="A script with a --clean option.")
    parser.add_argument("--clean", action="store_true", help="Clean up files instead of running main logic.")
    parser.add_argument("--count", action="store_true", help="Count how many response we have stored in the output file.")
    parser.add_argument("--compute", action="store_true", help="Compute the stance of the tweets.")

    args = parser.parse_args()

    if args.clean:
        clean(output_file)
    elif args.count:
        count(output_file)
    elif args.compute:
        run_main(output_file)
    else:
        raise ValueError("Please provide --clean, --count, or --compute argument.")
    
    io.info('Finishing script evaluate_stance_users.py ...')


if __name__ == '__main__':
    main()