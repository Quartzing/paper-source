import os
import requests
import feedparser
import re
import subprocess
from typing import List, Union, Dict
from paper_class import Paper


def contains_arxiv_reference(input_string: str) -> bool:
    """
    Check if the input string contains an arXiv reference.

    Args:
        input_string (str): The input string to check.

    Returns:
        bool: True if an arXiv reference is found, False otherwise.
    """
    # Define a regular expression pattern to match arXiv references
    arxiv_pattern = r'\barXiv:\d{4}\.\d{4,5}\b'

    # Use the re.search() function to search for the pattern in the input string
    match = re.search(arxiv_pattern, input_string)

    # If a match is found, return True; otherwise, return False
    return bool(match)

def download_link(url: str, filepath: str) -> None:
    """
    Download a file from a URL and save it to a specified filepath.

    Args:
        url (str): The URL to download the file from.
        filepath (str): The filepath to save the downloaded file.
    """
    print(f"Downloading {url} to {filepath}...")
    # Download the file using wget
    cmd = f"wget -U NoSuchBrowser/1.0 -O {filepath} {url}"
    try:
        subprocess.call(cmd, shell=True)
        print(f"The file '{filepath}' has been downloaded successfully.")
    except Exception as e:
        print("Failed to download the file.")
        print(e)
