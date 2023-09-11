import os
import re
from typing import List, Union, Dict
from tools import download_link
import requests
import feedparser
import subprocess
import arxiv
import logging
logging.basicConfig(level=logging.INFO)


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
            print('test')
            search.result.download_pdf()
            # download_link(url, file_path)

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
        year: int = self.publish_date.year
        return f'{author_list}, {year}. {self.title}. {self.url}'

    def get_APA_citation(self) -> str:
        """
        Get a citation in APA format.

        Returns:
            str: The APA citation.
        """
        return f'{self.authors[0]} et al. ({self.publish_date.year})'


def get_papers(search,
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
    output_directory: str = "arxiv_papers"
    os.makedirs(output_directory, exist_ok=True)

    results: Dict[str, Paper] = {}
    for result in search.results():
        paper: Paper = Paper(title=result.title,
                      summary=result.summary,
                      url=result.pdf_url,
                      authors=[author.name for author in result.authors],
                      publish_date=result.published)
        results[paper.title] = paper
        if download:
            paper.download(use_title=True)
            # result.download_pdf(dirpath=output_directory)

    return results
        

if __name__ == '__main__':
    search = arxiv.Search(
        query = "au:Yanrui Du AND ti:LLM",
        max_results = 3,
        sort_by = arxiv.SortCriterion.SubmittedDate,
        sort_order = arxiv.SortOrder.Descending
    )
    
    results: Dict[str, Paper] = get_papers(
        search,
        download=True,
    )

    for title, paper in results.items():
        print(paper.get_arxiv_citation())
        print(paper.get_APA_citation())
