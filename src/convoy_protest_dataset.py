import pandas as pd
import json
from enum import Enum
from src import paths_handler

from src.tweet import Tweet
from src.user import User
from src.place import Place

class DatasetType(Enum):
    """
    Enum representing different types of datasets.

    Attributes:
        MENTIONERS (int): Dataset containing information about mentioners.
        POSTERS (int): Dataset containing information about posters.
        RETWEETERS (int): Dataset containing information about retweeters.
    """
    ALL_TIMELINES = 1
    MENTIONERS = 2
    POSTERS = 3
    RETWEETERS = 4
    FLUTRUXKLAN = 5
    HOLDTHELINE = 6
    HONKHONK = 7
    TRUCKERCONVOY2022 = 8
    ALL_HASHTAGS=9
    ALL=10



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
    def get_dataset(data_type: DatasetType):
        paths = paths_handler.PathsHandler()

        if data_type == DatasetType.MENTIONERS:
            files = paths.get_json_filenames_from_folder('mentioners_path')
        elif data_type == DatasetType.POSTERS:
            files = paths.get_json_filenames_from_folder('posters_path')
        elif data_type == DatasetType.RETWEETERS:
            files = paths.get_json_filenames_from_folder('retweeters_path')
        elif data_type == DatasetType.FLUTRUXKLAN:
            files = paths.get_json_filenames_from_folder('flutruxklan_path')
        elif data_type == DatasetType.HOLDTHELINE:
            files = paths.get_json_filenames_from_folder('holdtheline_path')
        elif data_type == DatasetType.HONKHONK:
            files = paths.get_json_filenames_from_folder('honkhonk_path')
        elif data_type == DatasetType.TRUCKERCONVOY2022:
            files = paths.get_json_filenames_from_folder('truckerconvoy2022_path')
        elif data_type == DatasetType.ALL_TIMELINES:
            files = paths.get_json_filenames_from_folder('mentioners_path') + \
                        paths.get_json_filenames_from_folder('posters_path') + \
                            paths.get_json_filenames_from_folder('retweeters_path')
        elif data_type == DatasetType.ALL_HASHTAGS:
            files = paths.get_json_filenames_from_folder('flutruxklan_path') + \
                        paths.get_json_filenames_from_folder('holdtheline_path') + \
                            paths.get_json_filenames_from_folder('honkhonk_path') + \
                                paths.get_json_filenames_from_folder('truckerconvoy2022_path')
            
        elif data_type == DatasetType.ALL:
            files = paths.get_json_filenames_from_folder('mentioners_path') + \
                        paths.get_json_filenames_from_folder('posters_path') + \
                            paths.get_json_filenames_from_folder('retweeters_path') + \
                                paths.get_json_filenames_from_folder('flutruxklan_path') + \
                                    paths.get_json_filenames_from_folder('holdtheline_path') + \
                                        paths.get_json_filenames_from_folder('honkhonk_path') + \
                                            paths.get_json_filenames_from_folder('truckerconvoy2022_path')
    
        else:
            raise ValueError(f"Invalid DatasetType: {data_type}")

        all_tweets = []
        all_users = []
        all_places = []

        for filename in files:
            users, tweets, places = ConvoyProtestDataset._process_json_file(filename)
            all_tweets.extend(tweets)
            all_users.extend(users)
            all_places.extend(places)

        all_tweets = [Tweet.from_dict(tweet_dict) for tweet_dict in all_tweets]
        all_users = [User.from_dict(user_dict) for user_dict in all_users]
        all_places = [Place.from_dict(place_dict) for place_dict in all_places]


        return all_users, all_tweets, all_places

    @staticmethod
    def get_timelines_usernames():
        paths = paths_handler.PathsHandler()

        return pd.read_csv(
            paths.get_path('timeline_usernames_and_userids'),
            dtype={"user_id": str}
        )
        








