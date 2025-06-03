
from datetime import datetime
import pandas as pd
import sys
import os
import json
sys.path.append('..')
from src import io
from src.paths_handler import PathsHandler
from src.convoy_protest_dataset import DatasetType, ConvoyProtestDataset
import numpy as np 

def main():
    config = PathsHandler()
    script_config = config.get_variable('create-random-sample-tweets-configuration')
    data_folder = config.get_path('generated-data-folder')

    io.info(f'Using SEED=        {script_config["seed"]}.')
    io.info(f'Using SAMPLE_SIZE= {script_config["sample-size"]}.')
    io.info(f'Using OUTPUT_FILE= {script_config["output-filename"]}.')
    io.info(f'Using DATA_FOLDER= {data_folder}.')

    #  ========= Load user ID to username mapping: ==========
    with open(config.get_path('userid2usernames_map'), 'r', encoding='utf-8') as f:
        userid2username = json.load(f)

    output_file = os.path.join(data_folder, script_config['output-filename'])
    rng = np.random.default_rng(script_config['seed'])


    io.info('Loading Convoy Protest Dataset...')
    users, tweets, places = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL,
                                                             removed_repeated=True
                                                             )
    
    io.info(f'Loaded {len(users):,} users, {len(tweets):,} tweets, and {len(places):,} places.')

    # ========= Filter by date: ==========
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 3, 31)
    tweets = [tweet for tweet in tweets if start_date <= tweet.created_at <= end_date]
    io.info(f'Filtered tweets to {len(tweets):,} tweets between {start_date.date()} and {end_date.date()}.')

    # ========== Remove retweets: ========== 
    tweets = [tweet for tweet in tweets if not tweet.is_retweet]
    io.info(f'Tweet count with retweets removed:         {len(tweets):,}')

    # ========== Remove tweets with URL: ========== 
    tweets = [tweet for tweet in tweets if len(tweet.urls)==0]
    io.info(f'Tweet count with tweets with urls removed: {len(tweets):,}')

    # ========== Select random sample of tweets: ==========
    selected_tweets = rng.choice(tweets,
                                 size=script_config['sample-size'],
                                 replace=False)

    # ========== Prepare output data: ==========
    if any([len(userid2username.get(tweet.author_id, ['unknown']))>1 for tweet in selected_tweets]):
        io.warning('Some tweets have multiple usernames associated with the author ID. '
                   'Using the first username found for each author ID.')
    usernames = [userid2username.get(tweet.author_id, ['unknown'])[0] for tweet in selected_tweets]
    output_data = {
        'tweet_id': [tweet.id for tweet in selected_tweets],
        'created_at': [tweet.created_at.isoformat() for tweet in selected_tweets],
        'author_id': [tweet.author_id for tweet in selected_tweets],
        'username': usernames,
        'url': [f'https://x.com/{username}/status/{tweet.id}' 
                for tweet,username in zip(selected_tweets, usernames)],
        'text': [tweet.text.replace('\n', '\\n') for tweet in selected_tweets],
    }

    # ========== Save to CSV: ==========
    df = pd.DataFrame(output_data)
    df.to_csv(output_file, 
              index=False)
    io.info(f'Saved {len(df):,} tweets to {output_file}.')

if __name__ == '__main__':
    # obtain script name
    script_name = sys.argv[0].split('/')[-1]
    io.info(f'Starting script {script_name}...')
    main()
    io.info(f'Finishing script {script_name}...')