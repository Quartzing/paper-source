import os
import re
from typing import List, Union, Dict
from tools import download_link
import requests
import feedparser
import subprocess
import arxiv


class Paper(object):
    def __init__(self, title: str, summary: str, url: str, authors: List[str], publish_date: Union[str, int, float]):
        """
        Initialize a Paper object.

        Args:
            title (str): The title of the paper.
            summary (str): The summary or abstract of the paper.
            url (str): The URL where the paper can be downloaded.
            authors (List[str]): A list of author names.
            publish_date (Union[str, int, float]): The publication date of the paper.
        """
        self.title: str = self.sanitize_title(title)
        self.summary: str = summary
        self.url: str = url
        self.authors: List[str] = authors
        self.publish_date: Union[str, int, float] = publish_date

    def download(self, folder: str = 'downloads', use_title: bool = False) -> str:
        """
        Download the paper to a specified folder.

        Args:
            folder (str, optional): The folder where the paper will be saved. Defaults to 'downloads'.
            use_title (bool, optional): Whether to use the paper's title as the filename. Defaults to False.

        Returns:
            str: The filepath where the paper is saved.
        """
        url: str = self.url
        # Extract the file name from the URL
        if use_title:
            file_name: str = self.title
        else:
            file_name: str = url.split('/')[-1]
        os.makedirs(folder, exist_ok=True)
        file_path: str = os.path.join(folder, file_name)

        # Check if the file already exists locally
        if os.path.exists(file_path):
            print(f"The file '{file_path}' already exists locally.")
        else:
            download_link(url, file_path)

        return file_path

    def sanitize_title(self, title: str) -> str:
        """
        Sanitize the title by replacing invalid characters with underscores and removing newline characters.

        Args:
            title (str): The title to sanitize.

        Returns:
            str: The sanitized title.
        """
        # Replace invalid characters with underscores
        title = re.sub(r'[\/:*?"<>|]', '_', title)
        # Remove newline characters
        title = title.replace('\n ', '')
        return title

    def get_arxiv_citation(self) -> str:
        """
        Get a citation in arXiv format.

        Returns:
            str: The arXiv citation.
        """
        author_list: str = ', '.join(self.authors)
        year: int = self.publish_date.tm_year
        return f'{author_list}, {year}. {self.title}. {self.url}'

    def get_APA_citation(self) -> str:
        """
        Get a citation in APA format.

        Returns:
            str: The APA citation.
        """
        return f'{self.authors[0]} et al. ({self.publish_date.tm_year})'

def get_papers(search_results,
               download: bool = False) -> Dict[str, Paper]:
    """
    Search for papers on arXiv and optionally download them.

    Args:
        query (str): The search query. Use example `au:XXX AND ti:XXXX` 
        max_results (int): The maximum number of results to retrieve.
        download (bool, optional): Whether to download the papers. Defaults to False.
        sort_type (str, optional): The sorting type for the search results. Defaults to "SubmittedDate".
        sort_order (str, optional): The sorting order for the search results. Defaults to "Descending".

    Returns:
        Dict[str, Paper]: A dictionary of Paper objects with titles as keys.
    """
    print(f"Searching {query} from arxiv... (max #results: {max_results})")
    # Perform the arXiv search using the arXiv API
    # base_url: str = "http://export.arxiv.org/api/query?"
    # search_query: str = f"search_query=all:{query}&start=0&max_results={max_results}&sortBy={sort_type}&sortOrder={sort_order}"

    # response: requests.Response = requests.get(base_url + search_query)
    # feed: feedparser.FeedParserDict = feedparser.parse(response.text)

    results: Dict[str, Paper] = {}
    for result in search_results():
        paper_link: result.entry_id
        paper_link += '.pdf'
        paper: Paper = Paper(title=result.title,
                      summary=entry.summary,
                      url=paper_link,
                      authors=result.author
                      publish_date=result.published)
        results[paper.title] = paper
        if download:
            paper.download(use_title=True)

    return results
        
                   
    # Create a directory to store the downloaded papers
    output_directory: str = "arxiv_papers"
    os.makedirs(output_directory, exist_ok=True)

    # results: Dict[str, Paper] = {}
    # Loop through the search results and download papers
                   
    # for entry in feed.entries:
    #     paper_link: str = [link for link in entry.links if link.type == "application/pdf"][0].href
    #     paper_link += '.pdf'
    #     paper: Paper = Paper(title=entry.title,
    #                   summary=entry.summary,
    #                   url=paper_link,
    #                   authors=[author['name'] for author in entry.authors],
    #                   publish_date=entry.published_parsed)
    #     results[paper.title] = paper
    #     if download:
    #         paper.download(use_title=True)

    # return results

if __name__ == '__main__':
    results: Dict[str, Paper] = get_papers(
        query="LLM medical",
        max_results=10,
        download=False,
    )

    for title, paper in results.items():
        print(paper.get_arxiv_citation())
        print(paper.get_APA_citation())
