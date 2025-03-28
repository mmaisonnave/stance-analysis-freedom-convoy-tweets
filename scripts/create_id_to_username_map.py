"""
Module: create_id_to_username_map.py

This script extracts user ID to username mappings from the ConvoyProtestDataset 
and saves them to a JSON file.

Usage:
    Run the script to generate a JSON file containing the mapping.
"""

import sys
import json

sys.path.append('..')

from src.convoy_protest_dataset import DatasetType, ConvoyProtestDataset
from src.paths_handler import PathsHandler
from src import io  


def _find_duplicate_usernames(userid2username):
    """
    method to find if two users (with different user id) are associated with the same username

    example of input argument:
    userid2username = {
    1: ["alice", "alice123", "alice_wonder"],
    2: ["bob", "bobby", "bob_the_builder"],
    3: ["charlie", "charlie123", "alice"],  # "alice" appears under user 3
    4: ["dave", "davey", "dave123"]
}
    """
    username_map = {}  # Maps username to user_id(s)
    
    for user_id, usernames in userid2username.items():
        for username in usernames:
            if username in username_map:
                username_map[username].add(user_id)
            else:
                username_map[username] = {user_id}
    
    duplicates = {username: user_ids for username, user_ids in username_map.items() if len(user_ids) > 1}
    
    return duplicates



def main():
    """
    Main function to create a user ID to username mapping and save it to a JSON file.
    """
    io.info("Initializing paths handler.")
    paths_handler = PathsHandler()

    output_filename = paths_handler.get_path('userid2usernames_map')
    io.info(f"Output filename set to: {output_filename}")

    userid2usernames = {}
    io.info("Fetching dataset.")
    users, _, _ = ConvoyProtestDataset.get_dataset(data_type=DatasetType.ALL)
    io.ok("Dataset successfully retrieved.")
    io.info(f"Retrieved {len({user.id for user in users})} unique users")

    for user in users:
        if user.id not in userid2usernames:
            userid2usernames[user.id] = {user.username}
        else:
            userid2usernames[user.id].add(user.username)
    io.info(f"Processed {len(userid2usernames)} users.")


    userid2usernames = {user_id: list(usernames) for user_id, usernames in userid2usernames.items()}
    assert len(_find_duplicate_usernames(userid2usernames))==0, \
        'Different users (different user ids) associated with same username'

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(userid2usernames, f, ensure_ascii=False, indent=4)
        io.ok(f"Successfully saved user ID to username mapping to {output_filename}.")
    except (IOError, OSError) as e:
        io.error(f"Failed to save JSON file due to an I/O error: {e}")

if __name__ == "__main__":
    io.info("Starting execution of create_id_to_username_map.py.")
    main()
    io.ok("Execution completed successfully.")
