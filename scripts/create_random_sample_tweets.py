
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
from core.llms import OpenAIStanceDetector


def main():
    config = PathsHandler()

    # ========= INPUTS: ==========
    script_config = config.get_variable('create-random-sample-tweets-configuration')
    data_folder = config.get_path('generated-data-folder')

    io.info(f'Using SEED=        {script_config["seed"]}.')
    io.info(f'Using SAMPLE_SIZE= {script_config["target-sizes"]}.')
    io.info(f'Using OUTPUT_FILE= {script_config["output-filename"]}.')
    io.info(f"Using DATA_FOLDER= {data_folder}.")

    #  ========= Load user ID to username mapping: ==========
    with open(config.get_path('userid2usernames_map'), 'r', encoding='utf-8') as f:
        userid2username = json.load(f)
    io.info(f'Loaded {len(userid2username):,} user IDs to usernames mapping from {config.get_path("userid2usernames_map")}.')

    # ========== OUTPUT FILE: ==========
    output_file = os.path.join(data_folder, script_config['output-filename'])

    # ========== Stance Detector: ==========
    detector = OpenAIStanceDetector()


    # ====================================
    # ==== Tweet Sample WITHOUT URLs  ====
    # ====================================
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


    # ========== Remove replies: ==========
    tweets = [tweet for tweet in tweets if not tweet.is_reply]
    io.info(f'Tweet count with replies removed:          {len(tweets):,}')

    # ========== Remove retweets: ==========
    tweets = [tweet for tweet in tweets if not tweet.is_retweet]
    io.info(f'Tweet count with retweets removed:         {len(tweets):,}')

    # ========== Remove tweets with URL: ========== 
    tweets_with_no_url = [tweet for tweet in tweets if len(tweet.urls)==0]
    io.info(f'Tweet count with tweets with urls removed: {len(tweets_with_no_url):,}')
    
    # ========== Select random sample of tweets: ==========
    io.info(f'Selecting a random sample of {script_config["target-sizes"]} tweets with no URL...')
    target = script_config['target-sizes']  # 40% left, 20% neutral, 40% right
    selected_tweets = []
    stances = []
    indices = list(range(len(tweets_with_no_url)))

    while target[0] > 0 or target[1] > 0 or target[2] > 0:
        selected_index = rng.choice(indices)
        tweet = tweets_with_no_url[selected_index]
        indices.remove(selected_index)
        stance = detector.evaluate_tweet(tweet)
        io.info(f"STANCE: {stance['llm_response']:<10} | ({target[0]:3}, {target[1]:3}, {target[2]:3})")
        if stance['llm_response'] == 'left' and target[0] > 0:
            selected_tweets.append(tweet)
            target[0] -= 1
            stances.append('left')
        elif stance['llm_response'] == 'neutral' and target[1] > 0:
            selected_tweets.append(tweet)
            target[1] -= 1
            stances.append('neutral')
        elif stance['llm_response'] == 'right' and target[2] > 0:
            selected_tweets.append(tweet)
            target[2] -= 1
            stances.append('right')
        


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
        'stance': stances,
    }

    # ========== Save to CSV: ==========
    # Append '_no_urls' before the file extension, regardless of extension type
    base, ext = os.path.splitext(output_file)
    output_file = f"{base}_no_urls{ext}"

    df = pd.DataFrame(output_data)

    # shuffle the DataFrame rows using the `rng` default_rng
    df = df.sample(frac=1, random_state=rng).reset_index(drop=True)


    # Save version with 'stance' column
    df.to_csv(output_file, index=False)

    # Save version without 'stance' column
    output_file_no_stance = output_file.replace('.csv', '_no_stance.csv')
    df.drop(columns=['stance']).to_csv(output_file_no_stance, index=False)

    io.info(f'Saved tweets with no url: {len(df):,} tweets to {output_file}.')


    # # ====================================
    # # ====== Tweet Sample WITH URLs ======
    # # ====================================
    
    # ========== Now create sample with tweets with URL: ==========
    tweets_with_url = [tweet
                       for tweet in tweets if len(tweet.urls)>0 or \
                       (tweet.entities and 'urls' in tweet.entities and len(tweet.entities['urls'])>0)]
    
    io.info(f'Tweet count with tweets with urls: {len(tweets_with_url):,}')

    url_database_path = config.get_path('url-database')
    df = pd.read_csv(url_database_path)

    io.info(f'Loaded URL database with {len(df):,} URLs.')

    filtered_tweets_with_url = []
    for tweet in tweets_with_url:
        text_urls = tweet.urls
        metadata_urls = [url['expanded_url'] for url in tweet.entities['urls']] if tweet.entities and 'urls' in tweet.entities else []
        if any(url in df['URL'].values for url in text_urls) or \
           any(url in df['URL'].values for url in metadata_urls):
            filtered_tweets_with_url.append(tweet)
    io.info(f'After filtering only valid URLs from database: {len(filtered_tweets_with_url):,}')



    # ========== Select random sample of tweets: ==========
    target = script_config['target-sizes']  # 40% left, 20% neutral, 40% right
    selected_tweets = []
    stances = []
    indices = list(range(len(filtered_tweets_with_url)))

    while target[0] > 0 or target[1] > 0 or target[2] > 0:
        selected_index = rng.choice(indices)
        tweet = filtered_tweets_with_url[selected_index]
        indices.remove(selected_index)
        stance = detector.evaluate_tweet(tweet)
        io.info(f"STANCE: {stance['llm_response']:<10} | ({target[0]:3}, {target[1]:3}, {target[2]:3})")
        if stance['llm_response'] == 'left' and target[0] > 0:
            selected_tweets.append(tweet)
            target[0] -= 1
            stances.append('left')
        elif stance['llm_response'] == 'neutral' and target[1] > 0:
            selected_tweets.append(tweet)
            target[1] -= 1
            stances.append('neutral')
        elif stance['llm_response'] == 'right' and target[2] > 0:
            selected_tweets.append(tweet)
            target[2] -= 1
            stances.append('right')

        if not indices:
            io.warning('No more tweets to select from. Stopping selection process.')
            break

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
        'stance': stances,
    }

    # ========== Save to CSV: ==========
    # Append '_no_urls' before the file extension, regardless of extension type
    output_file = f"{base}_with_urls{ext}"

    df = pd.DataFrame(output_data)
    df.to_csv(output_file,
              index=False)
    
    output_file_no_stance = output_file.replace('.csv', '_no_stance.csv')
    df.drop(columns=['stance']).to_csv(output_file_no_stance, index=False)


    io.info(f'Saved tweets with url: {len(df):,} tweets to {output_file}.')







if __name__ == '__main__':
    # obtain script name
    script_name = sys.argv[0].split('/')[-1]
    io.info(f'Starting script {script_name}...')
    main()
    io.info(f'Finishing script {script_name}...\n\n')
