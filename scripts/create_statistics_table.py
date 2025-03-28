"""
This script creates a table with statistics about the dataset.
"""

import sys
import pandas as pd
from collections import Counter

sys.path.append('..')

from src.convoy_protest_dataset import DatasetType, ConvoyProtestDataset
from src.paths_handler import PathsHandler
from src import io  # Assuming io module is available for logging


def main():
    paths_handler = PathsHandler()

    # Define dataset types
    DATASET_TYPES = [
        DatasetType.POSTERS, 
        DatasetType.MENTIONERS, 
        DatasetType.RETWEETERS, 
        DatasetType.ALL_TIMELINES, 
        DatasetType.FLUTRUXKLAN, 
        DatasetType.HOLDTHELINE,
        DatasetType.HONKHONK, 
        DatasetType.TRUCKERCONVOY2022, 
        DatasetType.ISTANDWITHTRUCKERS, 
        DatasetType.ALL_HASHTAGS,
        DatasetType.ALL
    ]

    io.info("Starting dataset analysis and statistics generation...")

    rows = []

    for dataset_type in DATASET_TYPES:
        io.info(f"Processing dataset: {dataset_type}")

        users, tweets, places = ConvoyProtestDataset.get_dataset(data_type=dataset_type)

        if not tweets:
            io.debug(f"No tweets found for dataset {dataset_type}. Skipping...")
            continue

        io.debug(f"Loaded {len(tweets)} tweets for dataset {dataset_type}.")

        # Efficiently get unique tweets using a dictionary
        unique_tweets = {tweet.id: tweet for tweet in tweets}.values()
        io.debug(f"Filtered {len(unique_tweets)} unique tweets.")

        # Compute hashtag and mention counts
        hashtag_count = Counter(hashtag for tweet in unique_tweets for hashtag in tweet.hashtags)
        mention_count = Counter(mention for tweet in unique_tweets for mention in tweet.mentions)

        # Calculate statistics
        num_unique_tweets = len(unique_tweets)
        num_unique_authors = len({tweet.author_id for tweet in unique_tweets})
        num_tweets_with_url = sum(1 for tweet in unique_tweets if tweet.urls)
        num_retweets = sum(1 for tweet in unique_tweets if tweet.is_retweet)
        num_replies = sum(1 for tweet in unique_tweets if tweet.is_reply)
        num_with_text = sum(1 for tweet in unique_tweets if tweet.sanitized_text)

        # Handle division by zero
        def safe_percentage(numerator, denominator):
            return (numerator / denominator) if denominator else 0

        data = {
            'Dataset Split': [str(dataset_type)],
            'No. of unique tweets': [num_unique_tweets],
            'No. of unique authors': [num_unique_authors],
            '% tweets with URL': [safe_percentage(num_tweets_with_url, num_unique_tweets)],
            '% retweets': [safe_percentage(num_retweets, num_unique_tweets)],
            '% replies': [safe_percentage(num_replies, num_unique_tweets)],
            '% with text': [safe_percentage(num_with_text, num_unique_tweets)],
            'No. unique hashtags': [len(hashtag_count)],
            'Median tweet length': [pd.Series([len(tweet.sanitized_text) for tweet in unique_tweets]).median()],
            'Top 5 hashtags': ['; '.join(f'{tag}({count})' for tag, count in hashtag_count.most_common(5))],
            'Top 5 mentions': ['; '.join(f'{mention}({count})' for mention, count in mention_count.most_common(5))],
        }

        io.ok(f"Successfully processed statistics for dataset {dataset_type}.")

        rows.append(pd.DataFrame(data))

    # Concatenate all results into a single DataFrame
    final_df = pd.concat(rows, ignore_index=True)

    io.info("Final statistics table generated.")

    # Save the dataframe to CSV
    csv_path = paths_handler.get_path('statistics_table')
    final_df.to_csv(csv_path, index=False)

    io.ok(f"Statistics table saved successfully to {csv_path}.")


if __name__ == '__main__':
    main()