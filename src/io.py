"""
This module contains functions to print messages to the console and a log file,
without capturing third-party log messages.
"""

import sys
sys.path.append('..')

from src import paths_handler
import logging

log_filepath = paths_handler.PathsHandler().get_path('output_log')

# Create a custom logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # You control what gets logged

# Prevent propagation to root logger (avoids picking up 3rd party logs)
logger.propagate = False

# Create handlers
file_handler = logging.FileHandler(log_filepath)
console_handler = logging.StreamHandler()

# Create formatter and add to handlers
formatter = logging.Formatter('[%(asctime)s] [%(levelname)-7s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Attach handlers to the logger if they haven't been added already
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def info(message: str) -> None:
    """
    Log an information message.
    """
    logger.info(message)

def error(message: str) -> None:
    """
    Log an error message.
    """
    logger.error(message)

def warning(message: str) -> None:
    """
    Log a warning message.
    """
    logger.warning(message)

def debug(message: str) -> None:
    """
    Log a debug message.
    """
    logger.debug(message)

def ok(message: str) -> None:
    """
    Log an OK message (treated as INFO level).
    """
    logger.info(f"[  OK   ] {message}")
