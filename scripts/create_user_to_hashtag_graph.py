import json
import sys
sys.path.append('..')

from src.convoy_protest_dataset import DatasetType
from src.convoy_protest_dataset import ConvoyProtestDataset
from src.paths_handler import PathsHandler
from src import io  # Assuming an io handler module exists

def main():
    """
    Creates a user-to-hashtag graph from tweet data and saves it to a CSV file.
    """
    io.info("Initializing paths handler.")
    paths_handler = PathsHandler()

    for data_type in [DatasetType.FLUTRUXKLAN, DatasetType.HOLDTHELINE, DatasetType.HONKHONK, 
                      DatasetType.TRUCKERCONVOY2022, DatasetType.ISTANDWITHTRUCKERS]:
        io.info(f"Loading tweets dataset. Datatype={data_type}...")
        _, tweets, _ = ConvoyProtestDataset.get_dataset(data_type=data_type)
        
        io.info("Building user-to-hashtag graph.")
        graph = {}
        for tweet in tweets:
            user_hashtags = graph.setdefault(tweet.author_id, {})
            for hashtag in tweet.hashtags:
                user_hashtags[hashtag] = user_hashtags.get(hashtag, 0) + 1
        
        graph = {key: value for key, value in graph.items() if value}
        io.ok(f"Graph built with {len(graph)} users.")

        input_filename = paths_handler.get_path('userid2usernames_map')
        io.info(f"Loading user ID to username mappings from {input_filename}.")
        with open(input_filename, 'r', encoding='utf-8') as f:
            userid2usernames = json.load(f)

        outputfile = paths_handler.get_path('user2hashtag_graph_filename')

        assert outputfile.endswith('csv')
        data_type_name = str(data_type).lower()

        outputfile = f'{outputfile[:-4]}_' +data_type_name+ '.csv'


        io.info(f"Saving graph to {outputfile}.")
        with open(outputfile, 'w', encoding='utf-8') as outfile:
            outfile.write('username,hashtag,frequency\n')
            row_count = 0
            for user_id, hashtags in graph.items():
                if user_id in userid2usernames:
                    username = userid2usernames[user_id][0]
                    for hashtag, frequency in hashtags.items():
                        outfile.write(f'{username},{hashtag},{frequency}\n')
                        row_count += 1
            io.ok(f"Graph saved successfully with {row_count} entries.")

if __name__ == '__main__':
    io.info("Starting script execution.")
    main()
    io.info("Script execution finished.")
