from datetime import datetime
import pandas as pd
import json
from enum import Enum
from src import paths_handler
from itertools import chain
from typing import Dict, List, Optional

from src.tweet import Tweet
from src.user import User
from src.place import Place

class DatasetType(Enum):
    """
    Enum representing different types of datasets.

    Attributes:
        MENTIONERS (str): Dataset containing information about mentioners.
        POSTERS (str): Dataset containing information about posters.
        RETWEETERS (str): Dataset containing information about retweeters.
    """
    ALL_TIMELINES = "all_timelines"
    MENTIONERS = "mentioners"
    POSTERS = "posters"
    RETWEETERS = "retweeters"
    FLUTRUXKLAN = "flutruxklan"
    HOLDTHELINE = "holdtheline"
    HONKHONK = "honkhonk"
    TRUCKERCONVOY2022 = "truckerconvoy2022"
    ISTANDWITHTRUCKERS = "istandwithtruckers"
    ALL_HASHTAGS = "all_hashtags"
    ALL = "all"




class ConvoyProtestDataset:

    @staticmethod
    def _process_dict(elem_or_data, tweets, users, places):
        """

        Processes a single dictionary representing either a tweet or a collection of users, tweets, and places.

        If the input dictionary contains the key 'lang', it is treated as a single tweet and added to the `tweets` list.
        If the dictionary contains keys for 'users', 'tweets', and 'places', it is processed as a collection of data
        and the corresponding lists are updated with the respective values.
        
        
        If it is not a single tweet, then the dictionary could have this format: {'users': [...],
        'tweets': [...], 'places': [...]} where some of these keys could not be there.

        """
        # Process the data (either single element or list of elements)
        if 'lang' in elem_or_data:
            tweets.append(elem_or_data)
        elif 'users' in elem_or_data:
            users.extend(elem_or_data.get('users', []))
            tweets.extend(elem_or_data.get('tweets', []))
            places.extend(elem_or_data.get('places', []))

    @staticmethod
    def get_hashtag_tweets(dataset_type: DatasetType) -> list[Tweet]:
        """
        Retrieves tweets associated with a specific dataset type based on a predefined hashtag.
        Args:
            dataset_type (DatasetType): The type of dataset to filter tweets by.
        Returns:
            list[Tweet]: A list of tweets that contain the specified hashtag in their text.
        Raises:
            AssertionError: If the provided dataset_type is not one of the predefined types.
        """
        assert dataset_type in {DatasetType.FLUTRUXKLAN,
                                DatasetType.HOLDTHELINE,
                                DatasetType.HONKHONK,
                                DatasetType.TRUCKERCONVOY2022,
                                DatasetType.ISTANDWITHTRUCKERS
                                }
        dataset_type2hashtag = {
            DatasetType.FLUTRUXKLAN: '#FluTruxKlan',
            DatasetType.HOLDTHELINE: '#HoldTheLine',
            DatasetType.HONKHONK: '#HonkHonk',
            DatasetType.TRUCKERCONVOY2022: '#TruckerConvoy2022',
            DatasetType.ISTANDWITHTRUCKERS: '#IStandWithTruckers'
        }
        _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL,
                                                        removed_repeated=True)
        return [tweet
                for tweet in tweets
                if dataset_type2hashtag[dataset_type].lower() in tweet.text.lower()]

    @staticmethod
    def _process_json_file(json_filename):
        """
        Reads and processes a JSON file containing either a single dictionary or a list of dictionaries.

        If the JSON file contains a list, each dictionary in the list is processed individually, assuming each 
        dictionary represents a tweet or a collection of users, tweets, and places.
        
        If the JSON file contains a single dictionary, it is processed as a collection of users, tweets, and places.

        The method processes the file and returns three lists: one for users, one for tweets, and one for places.

        When the json has a dictionary, it is multiple users, tweets and places with this format:
         {'users': [...], 'tweets': [...], 'places': [...]}
         
        """
        tweets = []
        users = []
        places = []
        with open(json_filename, "r", encoding='utf-8') as file:
            data = json.load(file)

        # Skip empty data
        if data:

            # Process data if it's a list or a single dictionary
            if isinstance(data, list):
                for elem in data:
                    assert isinstance(elem, dict)
                    ConvoyProtestDataset._process_dict(elem, tweets, users, places)
            else:

                assert isinstance(data, dict)
                ConvoyProtestDataset._process_dict(data, tweets, users, places)

        return users, tweets, places

    @staticmethod
    def get_dataset(data_type: DatasetType, removed_repeated=False):
        paths = paths_handler.PathsHandler()

        # Map dataset types to respective folder paths
        folder_map = {
            DatasetType.ISTANDWITHTRUCKERS: 'istandwithtruckers_file',
            DatasetType.MENTIONERS: 'mentioners_path',
            DatasetType.POSTERS: 'posters_path',
            DatasetType.RETWEETERS: 'retweeters_path',
            DatasetType.FLUTRUXKLAN: 'flutruxklan_path',
            DatasetType.HOLDTHELINE: 'holdtheline_path',
            DatasetType.HONKHONK: 'honkhonk_path',
            DatasetType.TRUCKERCONVOY2022: 'truckerconvoy2022_path',
        }

        # Handle dataset types and combine files as necessary
        if data_type == DatasetType.ISTANDWITHTRUCKERS:
            tweets = ConvoyProtestDataset._transform_xlsx_to_tweets(
                paths.get_path(folder_map[DatasetType.ISTANDWITHTRUCKERS])
            )
            
            return [], [tweet for tweet in tweets if tweet.is_valid], []

        elif data_type in folder_map:
            files = paths.get_json_filenames_from_folder(folder_map[data_type])

        elif data_type == DatasetType.ALL_TIMELINES:
            files = chain(
                paths.get_json_filenames_from_folder('mentioners_path'),
                paths.get_json_filenames_from_folder('posters_path'),
                paths.get_json_filenames_from_folder('retweeters_path')
            )

        elif data_type == DatasetType.ALL_HASHTAGS:
            files = chain(
                paths.get_json_filenames_from_folder('flutruxklan_path'),
                paths.get_json_filenames_from_folder('holdtheline_path'),
                paths.get_json_filenames_from_folder('honkhonk_path'),
                paths.get_json_filenames_from_folder('truckerconvoy2022_path')
            )

        elif data_type == DatasetType.ALL:
            files = chain(
                paths.get_json_filenames_from_folder('mentioners_path'),
                paths.get_json_filenames_from_folder('posters_path'),
                paths.get_json_filenames_from_folder('retweeters_path'),
                paths.get_json_filenames_from_folder('flutruxklan_path'),
                paths.get_json_filenames_from_folder('holdtheline_path'),
                paths.get_json_filenames_from_folder('honkhonk_path'),
                paths.get_json_filenames_from_folder('truckerconvoy2022_path')
            )
        
        else:
            raise ValueError(f"Invalid DatasetType: {data_type}")

        # Process JSON files
        all_tweets = []
        all_users = []
        all_places = []

        for filename in files:
            users, tweets, places = ConvoyProtestDataset._process_json_file(filename)
            all_tweets.extend(tweets)
            all_users.extend(users)
            all_places.extend(places)

        # Create objects from dictionaries
        all_tweets = [Tweet.from_dict(tweet_dict) for tweet_dict in all_tweets]
        all_users = [User.from_dict(user_dict) for user_dict in all_users]
        all_places = [Place.from_dict(place_dict) for place_dict in all_places]

        if data_type == DatasetType.ALL or data_type == DatasetType.ALL_HASHTAGS:
            iswt_users, iswt_tweets, iswt_places =  ConvoyProtestDataset.get_dataset(
                data_type=DatasetType.ISTANDWITHTRUCKERS
            )
            # Adding IStandWithTrucker info to results:
            all_users.extend(iswt_users)
            all_tweets.extend(iswt_tweets)
            all_places.extend(iswt_places)
            
        # Tweets do not require to be filter by is_valid, the only dataset type with 
        # that problem is the ISTANDWITHTRUCKERS, which is handled above.
        
        if removed_repeated:
            all_tweets = ConvoyProtestDataset._remove_repeated_tweets(all_tweets)
            all_users = ConvoyProtestDataset._remove_repeated_users(all_users)
            all_places = ConvoyProtestDataset._remove_repeated_places(all_places)


        return all_users, all_tweets, all_places

    @staticmethod
    def _remove_repeated_places(places: List[Place]) -> List[Place]:
        new_list = []
        visited = set()
        for place in places:
            id_ = (place.id, place.country_code)
            if id_ not in visited:
                visited.add(id_)
                new_list.append(place)

        return new_list


    @staticmethod
    def _remove_repeated_users(users: List[User]) -> List[User]:
        new_list = []
        visited = set()
        for user in users:
            id_ = (user.id, user.created_at)
            if id_ not in visited:
                visited.add(id_)
                new_list.append(user)

        return new_list

    @staticmethod
    def _remove_repeated_tweets(tweets: List[Tweet]) -> List[Tweet]:

        new_list = []
        visited = set()
        for tweet in tweets:
            id_ = (tweet.id, tweet.text, tweet.author_id)
            if id_ not in visited:
                visited.add(id_)
                new_list.append(tweet)

        return new_list


    # @staticmethod
    # def get_dataset(data_type: DatasetType):
    #     paths = paths_handler.PathsHandler()

    #     if data_type == DatasetType.ISTANDWITHTRUCKERS:
    #         users = []
    #         places = []
    #         tweets = Tweet.transform_xlsx_to_tweets(paths.get_path('istandwithtruckers_file'))
    #         return users, list(filter(lambda tweet: tweet.is_valid, tweets)), places
            
    #     elif data_type == DatasetType.MENTIONERS:
    #         files = paths.get_json_filenames_from_folder('mentioners_path')
    #     elif data_type == DatasetType.POSTERS:
    #         files = paths.get_json_filenames_from_folder('posters_path')
    #     elif data_type == DatasetType.RETWEETERS:
    #         files = paths.get_json_filenames_from_folder('retweeters_path')
    #     elif data_type == DatasetType.FLUTRUXKLAN:
    #         files = paths.get_json_filenames_from_folder('flutruxklan_path')
    #     elif data_type == DatasetType.HOLDTHELINE:
    #         files = paths.get_json_filenames_from_folder('holdtheline_path')
    #     elif data_type == DatasetType.HONKHONK:
    #         files = paths.get_json_filenames_from_folder('honkhonk_path')
    #     elif data_type == DatasetType.TRUCKERCONVOY2022:
    #         files = paths.get_json_filenames_from_folder('truckerconvoy2022_path')
    #     elif data_type == DatasetType.ALL_TIMELINES:
    #         files = paths.get_json_filenames_from_folder('mentioners_path') + \
    #                     paths.get_json_filenames_from_folder('posters_path') + \
    #                         paths.get_json_filenames_from_folder('retweeters_path')
    #     elif data_type == DatasetType.ALL_HASHTAGS:
    #         files = paths.get_json_filenames_from_folder('flutruxklan_path') + \
    #                     paths.get_json_filenames_from_folder('holdtheline_path') + \
    #                         paths.get_json_filenames_from_folder('honkhonk_path') + \
    #                             paths.get_json_filenames_from_folder('truckerconvoy2022_path')
            
    #     elif data_type == DatasetType.ALL:
    #         files = paths.get_json_filenames_from_folder('mentioners_path') + \
    #                     paths.get_json_filenames_from_folder('posters_path') + \
    #                         paths.get_json_filenames_from_folder('retweeters_path') + \
    #                             paths.get_json_filenames_from_folder('flutruxklan_path') + \
    #                                 paths.get_json_filenames_from_folder('holdtheline_path') + \
    #                                     paths.get_json_filenames_from_folder('honkhonk_path') + \
    #                                         paths.get_json_filenames_from_folder('truckerconvoy2022_path')
    
    #     else:
    #         raise ValueError(f"Invalid DatasetType: {data_type}")

    #     all_tweets = []
    #     all_users = []
    #     all_places = []

    #     for filename in files:
    #         users, tweets, places = ConvoyProtestDataset._process_json_file(filename)
    #         all_tweets.extend(tweets)
    #         all_users.extend(users)
    #         all_places.extend(places)

    #     all_tweets = [Tweet.from_dict(tweet_dict) for tweet_dict in all_tweets]
    #     all_users = [User.from_dict(user_dict) for user_dict in all_users]
    #     all_places = [Place.from_dict(place_dict) for place_dict in all_places]


    #     return all_users, list(filter(lambda tweet: tweet.is_valid, all_tweets)), all_places

    @staticmethod
    def get_timelines_usernames():
        paths = paths_handler.PathsHandler()

        return pd.read_csv(
            paths.get_path('timeline_usernames_and_userids'),
            dtype={"user_id": str}
        )
    @staticmethod
    def get_relevant_users_duplicated_removed():
        paths = paths_handler.PathsHandler()

        return pd.read_csv(
            paths.get_path('relevant_user_db'),
            dtype={"user_id": str}
        )

    @staticmethod
    def get_userid_to_username_map():
        """
        Loads and returns a mapping of user IDs to usernames from a JSON file.
        """
        paths = paths_handler.PathsHandler()

        input_filename = paths.get_path('userid2usernames_map')

        with open(input_filename, 'r', encoding='utf-8') as f:
            userid2usernames = json.load(f)
        return userid2usernames
    
    # @staticmethod
    # def get_username_2_userid_map():
    #     """
    #     Loads and returns a mapping of user IDs to usernames from a JSON file.
    #     """
    #     paths = paths_handler.PathsHandler()

    #     input_filename = paths.get_path('userid2usernames_map')

    #     with open(input_filename, 'r', encoding='utf-8') as f:
    #         userid2usernames = json.load(f)

        # username2userid = {}
        # for user_id, usernames in userid2usernames.items():
        #     for username in usernames:
        #         username2userid[username]=user_id

    #     return username2userid

    @staticmethod
    def _parse_referenced_tweets(row):
        """
        Parse the referenced tweets from a row in the XLSX file.

        Used in _transform_xlsx_to_tweets only. 
        """
        if pd.notna(row['referenced_tweet_id']) and pd.notna(row['referenced_tweet_type']):
            return [{'type': row['referenced_tweet_type'], 'id': str(row['referenced_tweet_id'])}]
        return None


    @staticmethod
    def _transform_xlsx_to_tweets(xlsx_filepath: str) -> List["Tweet"]:
        """
        Transform an XLSX file containing tweet data into a list of Tweet objects.

        Warning: due to a problem in the XLSX file, the `Tweet.id` and `Tweet.author_id` might be wrong
        due to a truncating issue, I was given columns with id that were truncated to be too long integers.
        Example:
            real_id:        `1423712307616643072`
            column in xlsx: `1423712307616640000` (last four digits truncated to zero).
        """

        userid2usernames = ConvoyProtestDataset.get_userid_to_username_map()

        # Flip userid2usernames map to username2userid:
        # Because I cannot trust the author_id, I need to use the username which I can trust to bring
        # the real id from the User database we have (built from json not from xlsx).
        # So, our reputable source of user ids is: 
        username2userid = {
            username: user_id
            for user_id, usernames in userid2usernames.items()
            for username in usernames
        }


        tweets = []
        df = pd.read_excel(xlsx_filepath)
        
        for _, row in df.iterrows():
            tweet = Tweet(
                lang=row['language'],
                # Here I have to either pick if I would store an `N/A` when I cannot get the id from a reputable source, 
                # or take the author id from the xlsx file (which there is a high chance is wrong).

                author_id=str(username2userid[row['username']]) if row['username'] in  username2userid else 'N/A', # From reputable source (username2userid, computed from Users list)
                # author_id=str(row['userid']),                                                                         # From xlsx
                public_metrics={
                    'retweet_count': int(row['retweet_count']),
                    'reply_count': int(row['reply_count']),
                    'like_count': int(row['like_count']),
                    'quote_count': int(row['quote_count']),
                    'bookmark_count': 0,  # Not available in XLSX, set to 0
                    'impression_count': 0  # Not available in XLSX, set to 0
                },
                created_at=datetime.strptime(row['date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                id=str(row['tweet_id']),
                conversation_id=str(row['tweet_id']) if pd.isna(row['in_reply_to_tweet_id']) else int(row['in_reply_to_tweet_id']),
                text=row['text'],
                possibly_sensitive=str(row['possibly_sensitive']).lower() == 'true',
                referenced_tweets=ConvoyProtestDataset._parse_referenced_tweets(row),
                author_username=row['username']
            )
            tweets.append(tweet)
        
        return tweets

    # @staticmethod
    # def _get_userid_to_username_from_xlsx():
    #     paths = paths_handler.PathsHandler()

    #     xlsx_filepath = paths.get_path('istandwithtruckers_file')
    #     df = pd.read_excel(xlsx_filepath)
        
    #     userid2username = {}
    #     for _, row in df.iterrows():
    #         username = row['username']
    #         userid = row['userid']

    #         if not username in userid2username:
    #             userid2username[userid] = username
    #         else:
    #             assert userid2username[userid] == username

    #     return userid2username
