import os
import requests
import feedparser
import re
import subprocess


def contains_arxiv_reference(input_string: str) -> bool:
    # Define a regular expression pattern to match arXiv references
    arxiv_pattern = r'\barXiv:\d{4}\.\d{4,5}\b'

    # Use the re.search() function to search for the pattern in the input string
    match = re.search(arxiv_pattern, input_string)

    # If a match is found, return True; otherwise, return False
    if match:
        return True
    else:
        return False


def download_link(url: str, filepath: str):
    print(f"Downloading {url} to {filepath}...")
    # Download the file using wget
    cmd = f"wget -U NoSuchBrowser/1.0 -O {filepath} {url}"
    try:
        subprocess.call(cmd, shell=True)
        print(f"The file '{filepath}' has been downloaded successfully.")
    except Exception as e:
        print("Failed to download the file.")
        print(e)

class Paper(object):
    def __init__(self,
                 title: str,
                 summary: str,
                 url: str,
                 authors: list,
                 publish_date):
        self.title = self.sanitize_title(title)
        self.summary = summary
        self.url = url
        self.authors = authors
        self.publish_date = publish_date

    def download(self, folder: str='downloads', use_title: bool=False):
        url = self.url
        # Extract the file name from the URL
        if use_title:
            file_name = self.title
        else:
            file_name = url.split('/')[-1]
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, file_name)

        # Check if the file already exists locally
        if os.path.exists(file_path):
            print(f"The file '{file_path}' already exists locally.")
        else:
            download_link(url, file_path)

        return file_path

    # Define a function to sanitize titles
    def sanitize_title(self, title):
        # Replace invalid characters with underscores
        title = re.sub(r'[\/:*?"<>|]', '_', title)
        # Remove newline characters
        title = title.replace('\n ', '')
        return title

    def get_arxiv_citation(self):
        author_list = ', '.join(self.authors)
        year = self.publish_date.tm_year
        return f'{author_list}, {year}. {self.title}. {self.url}'

    def get_APA_citation(self):
        return f'{self.authors[0]} et al. ({self.publish_date.tm_year})'


def get_papers(query: str,
               max_results: int,
               download: bool=False,
               sort_type: str="relevance",
               sort_order: str="descending"):
    print(f"Searching {query} from arxiv... (max #results: {max_results})")
    # Perform the arXiv search using the arXiv API
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{query}&start=0&max_results={max_results}&sortBy={sort_type}&sortOrder={sort_order}"

    response = requests.get(base_url + search_query)
    feed = feedparser.parse(response.text)

    # Create a directory to store the downloaded papers
    output_directory = "arxiv_papers"
    os.makedirs(output_directory, exist_ok=True)

    results = {}
    # Loop through the search results and download papers
    for entry in feed.entries:
        # print(entry)
        paper_link = [link for link in entry.links if link.type == "application/pdf"][0].href
        paper_link += '.pdf'
        paper = Paper(title=entry.title,
                     summary=entry.summary,
                     url=paper_link,
                     authors=[author['name'] for author in entry.authors],
                     publish_date=entry.published_parsed)
        results[paper.title] = paper
        if download:
            paper.download(use_title=True)

    return results

if __name__ == '__main__':
    results = get_papers(
        query="LLM medical",
        max_results=10,
        download=False,
    )
    
    for title, paper in results.items():
        print(paper.get_citation())
        print(paper.get_APA_citation())
