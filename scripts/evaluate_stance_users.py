import argparse
import numpy as np
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
    SAMPLE_SIZE = 100
    SEED=2916376554

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


    author_ids = {author_id for author_id, count in
                  Counter([tweet.author_id for tweet in tweets ]).items()
                  if count>=detector.max_tweet_count}

    io.info(f'Number of users with more than {detector.max_tweet_count} tweets = {len(author_ids)}.')

    results = []

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as file:
            results = json.load(file)

    already_proccessed_ids = {result_item['author_id'] for result_item in results}
    
    io.info(f'elements to process:         {len(author_ids)}')
    io.info(f'already processed elements:  {len(already_proccessed_ids)}')
    author_ids = list(author_ids.difference(already_proccessed_ids))
    io.info(f'Elements left to process:    {len(author_ids)}')


    rng = np.random.default_rng(seed=SEED)

    rng.shuffle(author_ids)

    SAMPLE_SIZE=min(SAMPLE_SIZE, len(author_ids))
    for author_id in author_ids[:SAMPLE_SIZE]:
        tweets_from_user = [tweet for tweet in tweets if tweet.author_id==author_id]
        result = detector.evaluate_user(tweets_from_user)
        assert result['author_id'] == author_id
        results.append(result)

    io.info(f'Finished processing users, computed {len(results)} results.')
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    io.info('Results saved to disk.')

def count(output_file: str) -> None:
    counter = {}
    length = 0
    if os.path.exists(output_file):

        with open(output_file, 'r', encoding='utf-8') as file:
            results = json.load(file)

        counter = Counter([result['llm_response']['score'] for result in results])
        length = len(results)
    io.info(f'Count of results: {length}')
    io.info(f'Count of results: {counter}')
        
def main():
    config = PathsHandler()

    output_file = config.get_path('user-evaluation-output')
    io.info(f'Script will store results in {output_file}')

    io.info('Starting script evaluate_stance_users.py ...')
    parser = argparse.ArgumentParser(description="A script with a --clean option.")

    parser.add_argument("--clean", action="store_true", help="Clean up files instead of running main logic.")
    parser.add_argument("--count", action="store_true", help="Count how many response we have stored in the output file.")
    parser.add_argument("--compute", action="store_true", help="Compute the stance of the tweets.")

    args = parser.parse_args()

    if args.clean:
        clean(output_file)
    elif args.compute:
        run_main(output_file)
    elif args.count:
        count(output_file)
    else:
        raise ValueError("Invalid argument. Use --clean, --count, or --compute.")
    
    io.info('Finishing script evaluate_stance_users.py ...')


if __name__ == '__main__':
    main()