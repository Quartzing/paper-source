import os
import requests
import feedparser
import re
import subprocess
from typing import List, Union, Dict


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

def download_link(url: str, filepath: str, max_retry: int = 3) -> None:
    """
    Download a file from a URL and save it to a specified filepath.

    Args:
        url (str): The URL to download the file from.
        filepath (str): The filepath to save the downloaded file.
        max_retry (int): The max number of retrying.
    
    Raises:
        ValueError: when max_retry <= 0.
        ConnectionError: when downloading failed after max_retry times of retrying.
    """
    if max_retry <= 0:
        raise ValueError(f"Invalid max retry: {max_retry}")
    # Download the file with retrying.
    for idx, retry in enumerate(range(max_retry)):
        print(f"[{idx + 1}/{max_retry}] Trying to download {url} to {filepath}...")
        response = requests.get(url)
        if (response.ok):
            with open(filepath, 'wb') as f: 
                f.write(response.content)
            print(f"Done.")
            return
        print(f"Failed to download {url} with response code: {response.status_code}")

    raise ConnectionError(f"Failed to download {url} with max {max_retry} retries.")

if __name__ == '__main__':
    download_link(
        url='http://arxiv.org/pdf/2309.12314v11',
        filepath='test_file.pdf',
        max_retry=2,
    )
