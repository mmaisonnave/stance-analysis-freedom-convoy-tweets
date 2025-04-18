import pandas as pd

import sys
sys.path.append('..')

from src.convoy_protest_dataset import DatasetType
from src.convoy_protest_dataset import ConvoyProtestDataset
from src import paths_handler
from src import io

def main():
    paths = paths_handler.PathsHandler()
    io.info('Starting create_tweet_df.py script...')
    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL)
    io.info(f'Loaded {len(tweets):,} tweets from ConvoyProtestDataset')

    visited = set()
    unique_tweets = []
    for tweet in tweets:
        if not (tweet.id, tweet.author_id, tweet.text ) in visited:
            visited.add((tweet.id, tweet.author_id, tweet.text))
            unique_tweets.append(tweet)
    del(tweets)
    del(visited)
    io.info(f'Found {len(unique_tweets):,} unique tweets')

    output_path = paths.get_path('tweet_dataframe')
    io.info(f'Writing unique tweets to {output_path}')
    
    pd.DataFrame({
        'id': [tweet.id for tweet in unique_tweets],
        'author_id': [tweet.author_id for tweet in unique_tweets],
        'date': [tweet.created_at for tweet in unique_tweets],
    }).to_csv(output_path,
              index=False)

    io.ok('Done!')

if __name__ == "__main__":
    main()