"""
This module contains functions to print messages to the console.
"""
import datetime
def info(message:str)->None:
    """
    Print an information message.
    """
    print(f'[{datetime.datetime.now()}] [ INFO  ]', message)

def error(message:str)->None:
    """
    Print an error message.
    """
    print(f'[{datetime.datetime.now()}] [ ERROR ]', message)

def warning(message:str)->None:
    """
    Print a warning message.
    """
    print(f'[{datetime.datetime.now()}] [WARNING]', message)

def debug(message:str)->None:
    """
    Print a debug message.
    """
    print(f'[{datetime.datetime.now()}] [ DEBUG ]', message)

def ok(message:str)->None:
    """
    Print an OK message.
    """
    print(f'[{datetime.datetime.now()}] [  OK   ]', message)
