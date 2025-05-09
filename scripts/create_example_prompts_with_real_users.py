import numpy as np
from collections import Counter
import sys
sys.path.append('..')

from src import io
from src.paths_handler import PathsHandler
from src.convoy_protest_dataset import ConvoyProtestDataset, DatasetType



def main():
    SEED = 3130352397
    USER_SAMPLE_SIZE=5
    TWEET_SAMPLE_SIZE=30
    io.info('')
    io.info('-'*100)
    io.info('Starting script "create_example_prompts_with_real_users.py"...')

    config = PathsHandler()

    improved_prompt = config.get_prompt('chatgpt_improved_prompt')


    _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL, removed_repeated=True)
    
    io.info(f'Retrieved {len(tweets):,} unique tweets.')

    tweets = [tweet  for tweet in tweets if not tweet.is_retweet]

    io.info(f'Retweets removed. We now have: {len(tweets):,} unique tweets.')


    tweets = [tweet  for tweet in tweets if len(tweet.urls)==0]

    io.info(f'Tweets with URL removed. Now we have: {len(tweets):,} unique tweets.')


    df = ConvoyProtestDataset.get_relevant_users_duplicated_removed()

    user_ids = set(df['user_id'])
    usernames = set(df['username'])
    userid2username = {userid:username for userid, username in zip(user_ids, usernames)}


    # ========== Removing user_ids from df for who we do not have  a tweet.author_id entry ==========
    user_ids = [user_id for user_id in user_ids if user_id in {tweet.author_id for tweet in tweets}]
    io.info(f'Number of relevant users (in df) for who we have a tweet (author_id)= {len(user_ids)}')


    # ========== Removing tweets from irrelevant users (no authored any tweets: tweet.author_id) ==========
    tweets = [tweet for tweet in tweets if tweet.author_id in user_ids]
    io.info(f'Number of tweets from the {len(user_ids)} relevant users is {len(tweets):,} tweets')


    freq = Counter([tweet.author_id for tweet in tweets])

    freq_repr = [f'<{id_}: {count}>' for id_, count in freq.items()]
    io.info(f'freq= [{freq_repr[0]}, {freq_repr[1]},..., {freq_repr[-1]} ]')

    users_with_more_30_tweets = [id_ for id_,count in freq.items() if count>=30]

    io.info(f'len(users_with_more_100_tweets)={len(users_with_more_30_tweets)}')



    # ========== Randomly sampling from the relevant users with 100+ tweets authored ==========
    rng = np.random.default_rng(seed=SEED)

    selected_users = rng.choice(users_with_more_30_tweets,
                                size=USER_SAMPLE_SIZE,
                                replace=False
                                )

    tweets = [tweet for tweet in tweets if tweet.author_id in set(selected_users)]
    io.info(f'Relevant tweets for the {USER_SAMPLE_SIZE} randomly selected users= {len(tweets)}')



    # ========== SAVING TO DISK ==========
    with open(config.get_path('example-user-timelines'), 'w', encoding='utf-8') as writer:

        for user_id in selected_users:
            io.info('')
            io.info(f'user_id={user_id:20} ({userid2username[user_id]})')
            writer.write(f'user_id={user_id:20} ({userid2username[user_id]})\n')
            sample_author_tweets = rng.choice([tweet for tweet in tweets if tweet.author_id==user_id],
                                    size=TWEET_SAMPLE_SIZE,
                                    replace=False
                                    )
            for ix, tweet in enumerate(sample_author_tweets):
                io.info(f'tweet {1+ix}: ' + tweet.text.replace('\n', '. '))
                writer.write(f'tweet {1+ix}: ' + tweet.text.replace('\n', '. ') + '\n')
            writer.write('\n\n')

    io.info('Finishing script "create_example_prompts_with_real_users.py"...')


if __name__ == "__main__":
    main()