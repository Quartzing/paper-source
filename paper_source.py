import openai
import os
from typing import Dict, List
import uuid
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from tools import *
from paper_class import Paper
from abc import ABC, abstractmethod


class PaperSource(ABC):
    def __init__(self, openai_api_key: str):
        """
        Initializes with a dictionary of papers and an OpenAI API key.

        Args:
            openai_api_key (str): The OpenAI API key for text embeddings.
        """
        self.papers_: Dict[str, Paper] = []

        # Get embedding from OpenAI.
        embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # UUID4: Generates a random UUID in UUID class type.
        db_uuid = str(uuid.uuid4())
        # Compute embeddings for each chunk and store them in the database. Each with a unique id to avoid conflicts.
        print(f'Initiating vectordb {db_uuid} with {len(doc_list)} documents from {len(self.papers_)} papers.')
        """ Initiallize a vector store.
        Vector store elements are structured as follows:
        [
            'embedding': page_info,
            '[122143,123213,346346,34325234]': {
                page_content: 'LLM XXX',
                metadata: {
                    source: 'title ',
                    page: int,
                },
            },
        ]
        """
        self.db_: Chroma = Chroma(
            embedding_function=embedding,
            collection_name=db_uuid,
        )

    def add_papers(self, papers: dict[str, Paper]):
        """Add a paper to the object.
        Args:
            papers (Dict[str, Paper]): A dictionary containing paper titles as keys and object of class Paper as values.
        """
        self.papers_.update(papers)
        for _, paper in papers.items():
            self.add_paper(paper)

    def add_paper(self, paper: Paper):
        """Add a single paper to the source."""
        docs = self._process_paper(paper)  # Extract the PDF into chunks and append them to the doc_list.
        self.db_.add_documents(documents=docs)

    def papers(self) -> Dict[str, Paper]:
        """
        Returns the dictionary of papers.

        Returns:
            Dict[str, Paper]: A dictionary containing paper titles as keys and Paper objects as values.
        """
        return self.papers_

    def get_paper(self, title: str) -> Paper:
        """Returns the paper with the given title."""
        return self.papers_[title]

    @abstractmethod
    def _process_paper(self, paper: Paper) -> List[Document]:
        """
        Process the paper.

        Args:
            paper (Paper): A Paper object representing the paper to be processed.

        Returns:
            List[Document]: A list of Document objects, each containing a text chunk with metadata.
        """
        raise NotImplementedError("The _process_paper() function is not implemented.")
        pass

    def retrieve(self, query: str, num_retrieval: int | None =None) -> List[Document]:
        """
        Search for papers related to a query using text embeddings and cosine distance.

        Args:
            query (str): The query string to search for related papers.

        Returns:
            List[Document]: A list of Document objects representing the related papers found.
        """
        print(f'Searching for related works of: {query}...')
        if not num_retrieval:
            num_retrieval = len(self.papers_)
        sources: List[Document] = self.db_.similarity_search(query, k=num_retrieval)
        print(f'{len(sources)} sources found.')
        return sources
