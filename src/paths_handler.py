"""
paths_handler.py

This module provides a class for handling file paths stored in a YAML configuration file. 
It reads the configuration once during initialization and provides methods to retrieve 
specific paths.
"""

import os
import yaml

class PathsHandler:
    """
    A class to handle file paths stored in a YAML configuration file.

    This class loads the configuration once upon initialization and provides methods 
    to retrieve specific paths from the configuration.

    Attributes:
        CONFIGURATION_PATH (str): Path to the YAML configuration file.
        _config (dict): Dictionary storing the loaded configuration.
    """
    CONFIGURATION_PATH = "../config/paths.yaml"

    def __init__(self,):
        """
        Initializes the PathsHandler instance by loading the YAML configuration file.
        
        Raises:
            FileNotFoundError: If the configuration file is missing.
            yaml.YAMLError: If there's an issue parsing the YAML file.
        """
        with open(PathsHandler.CONFIGURATION_PATH, 'r', encoding='utf-8') as file:
            self._config = yaml.safe_load(file)['paths']

    # @property
    # def repository_path(self,):
    #     """
    #     Retrieves the repository path from the configuration.

    #     Returns:
    #         str: The repository path specified in the configuration file.
        
    #     Raises:
    #         KeyError: If 'repository_path' is not found in the configuration.
    #     """

    #     return self._config['repository_path']

    def get_path(self, path_key):
        if path_key=='repository_path':
            return self._config['repository_path'] 
        else:
            return os.path.join(self._config['repository_path'], self._config[path_key])

    def get_json_filenames_from_folder(self, path_key):
        path = self.get_path(path_key)
        files = []
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                filename = os.path.join(dirpath, filename)
                if filename.lower().endswith('json'):
                    files.append(filename)
        return files

    # @property
    # def metioners_path(self,):
    #     return os.path.join(self.repository_path, self._config['mentioners_path'])

    # @property
    # def posters_path(self,):
    #     return os.path.join(self.repository_path, self._config['posters_path'])

    # @property
    # def retweeters_path(self,):
    #     return os.path.join(self.repository_path, self._config['retweeters_path'])