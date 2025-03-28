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

    io.info(f'df shape: {df.shape}')

    userid2source = {}
    username2source = {}
    userid2username = {}
    for userid, username, source in zip(df['user_id'].values, df['username'], df['source'].values):
 
        if not pd.isna(userid):
            # Store ID information
            if userid not in userid2source:
                userid2source[str(userid)] = {source} 
            else:
                userid2source[str(userid)].add(source)
        
        if username not in username2source:
            username2source[username] = {source}
        else:
            username2source[username].add(source)
        

        if not pd.isna(userid):
            if userid in userid2username:
                assert not pd.isna(username)
                assert userid2username[userid]==username, f'{userid2username[userid]}!={username}'

            userid2username[userid]=username

    # userid2source = {k: tuple(v) for k, v in userid2source.items()}
    # username2source = {k: tuple(v) for k, v in username2source.items()}

    io.debug(f'len(userid2source)={len(userid2source)}')
    io.debug(f'len(username2source)={len(username2source)}')

    io.info('Obtaining User db from ConvoyProtestDataset module ...')
    users, tweets, places = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL)

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
        if str(user.id) in userid2source or user.username in username2source:
            # User is relevant, we need to store in relevant_user list:
            source = set()
            if str(user.id) in userid2source:
                source = source.union(userid2source[str(user.id)])
            if user.username in username2source:
                source = source.union(username2source[user.username])
            source = sorted(source)

            relevant_users.append(
                (str(user.id), user.username, tuple(source))
            )

    # ADDITIONAL CODE, UNUSED.
    # Originally created to see if there are author ids (tweet.author_id) in the 
    # List of tweets that are present in the list of relevant usernames and userids (df)
    # however, from the Tweet.author_id we cannot know the username, and that leds to 
    # incosistencies, since we cannot know if the original username is the one we have in
    # the DF or it is just a mistake. Therefore, we are only using userid and usernames
    # that we found in the users list of User objects if either the user id or username is
    # present in the DF (code above)

    # unique_ids_in_relevant_users = {user[0] for user in relevant_users}
    # unique_username_in_relevant_users = {user[1] for user in relevant_users}

    # # Check for each tweet, if it has a relevant author_id it the user has to be 
    # # in our db of relevant users.
    # for tweet in tweets:
    #     if str(tweet.author_id) in userid2source and \
    #         not str(tweet.author_id) in unique_ids_in_relevant_users:
    #         # User associated with id `author_id` is relevant, but we don't have it
    #         # in list of relevant users, we must store it.
    #         # Although we don't have their username
    #         username = "N/A"
    #         if str(tweet.author_id) in userid2username:
    #             username = userid2username[str(tweet.author_id)]
    #         if username in unique_username_in_relevant_users:
    #             username=f'{username}(repeated)'
    #         relevant_users.append(
    #             (tweet.author_id, username, tuple(userid2source[str(tweet.author_id)]))
    #             )
    # END OF ADDITIONAL CODE.

    # Traverse tweet list to find first tweet and last tweet for each user, also
    # begin, tweet count, end,


    relevant_users = list(set(relevant_users))

    author_id2data = {}
    relevant_ids = {id_ for id_, _,_ in relevant_users}

    for tweet in tweets:
        if str(tweet.author_id) in author_id2data and str(tweet.author_id) in relevant_ids:
            begin, tweet_count, end = author_id2data[str(tweet.author_id)]
            tweet_count+=1
            date = tweet.created_at
            
            assert not date is None
            begin = min(begin, date)
            end = max(end, date)

            author_id2data[str(tweet.author_id)]=(begin, tweet_count, end)
        else:
            author_id2data[str(tweet.author_id)] = (tweet.created_at,
                                                    0,
                                                    tweet.created_at
                                                    )
        

    relevant_users = [(user_id, username, source, *author_id2data[str(user_id)])
                     for user_id, username, source in relevant_users]


    # Sorting by tweet count, from more tweets to less tweets
    io.info('Sorting....')
    relevant_users = sorted(relevant_users, key = lambda x: x[4], reverse=True)

    result_df = pd.DataFrame(relevant_users,
                            columns=['user_id',
                                     'username',
                                     'sources',
                                     'first tweet',
                                     'tweet count',
                                     'last tweet'
                                     ]
                            )
    
    result_df.to_csv(
        paths.get_path('relevant_user_db'),
        index=False
        )
    io.ok('Finished creating relevant users database.')

if __name__ == "__main__":
    main()