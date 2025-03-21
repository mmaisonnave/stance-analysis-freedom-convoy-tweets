"""
This script creates a database of relevant users.

It uses the file `user_timelines_usernames_and_userids.csv` to obtain the list of 
relevant users (username, userids, and sources (either posters, mentioners, or retweeters)).

It then uses the `ConvoyProtestDataset` class to obtain the list of all users,
and all tweets in the dataset (329K+ unique tweets, 46K+ unique users, 12 unique places).
It takes the dataset from the `ALL_TIMELINES` data type (posters, mentioners, retweeters).


The script iterates over all users in the dataset and checks if the user is part of the
relevant users database. If the user is part of the relevant users database, it stores
the user_id, username, and sources in a list.

Finally, it creates a DataFrame from the list and stores it in a CSV file.


"""
import sys
import pandas as pd

sys.path.append('..')

from src.convoy_protest_dataset import DatasetType
from src.convoy_protest_dataset import ConvoyProtestDataset
from src.convoy_protest_dataset import paths_handler
from src import io

def main():
    io.info('Creating relevant users database...')
    paths = paths_handler.PathsHandler()
    df = ConvoyProtestDataset.get_timelines_usernames()
    usernames_in_df = set(df['username'].values)
    userids_in_df = set(df['user_id'].values)

    io.info(f'df shape: {df.shape}')

    username2source = {}
    for username, source in zip(df['username'].values, df['source'].values):
        if username not in username2source:
            username2source[username] = set([source])
        else:
            username2source[username].add(source)
            
    username2source = {k: tuple(v) for k, v in username2source.items()}

    io.info(f'Obtaining User db from ConvoyProtestDataset module ...')
    users, tweets, places = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL_TIMELINES)

    io.info(f'len(users): {len(users)}')
    io.info(f'len(tweets): {len(tweets)}')
    io.info(f'len(places): {len(places)}')

    io.info(f'len unique users: {len(set([user.id for user in users]))}')
    io.info(f'len unique tweets: {len(set([tweet.id for tweet in tweets]))}')
    io.info(f'len unique places: {len(set([place.id for place in places]))}')

    io.info('For each user in database, checking if it is part of relevant users. ')
    io.info('Storing userid, username, sources')
    
    relevant_users=[]
    for user in users:
        if str(user.id) in userids_in_df:
            relevant_users.append((user.id, user.username, tuple(username2source[user.username])))
        
        if user.username in usernames_in_df:
            relevant_users.append((user.id, user.username, tuple(username2source[user.username])))

    unique_ids_in_relevant_users = set([user[0] for user in relevant_users])

    # Check for each tweet, if it has a relevant author_id it the user has to be 
    # in our db of relevant users.
    for tweet in tweets:
        if str(tweet.author_id) in set([str(id) for id in userids_in_df]):
            # if author of a tweet is relevant, it has to exist in our 
            # db of relevant users (the db with a tuple of user_id, username, sources)
            assert tweet.author_id in unique_ids_in_relevant_users, \
                        "relevant author_id not in our db of relevant users"


    result_df = pd.DataFrame(list(set(relevant_users)),
                            columns=['user_id', 'username', 'sources']
                            )
    
    result_df.to_csv(
        paths.get_path('relevant_user_db'),
        index=False
        )
    io.ok('Finished creating relevant users database.')

if __name__ == "__main__":
    main()