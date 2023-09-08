import openai
import os
from typing import Dict, List
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from tools import *


class PaperSource:
    def __init__(self, papers: Dict[str, Paper], openai_api_key: str):
        """
        Initializes a PaperSource object with a dictionary of papers and an OpenAI API key.

        Args:
            papers (Dict[str, Paper]): A dictionary containing paper titles as keys and object of class Paper as values.
            openai_api_key (str): The OpenAI API key for text embeddings.
        """
        self.papers_: Dict[str, Paper] = papers
        doc_list: List[Document] = []
        for title, paper in papers.items():
            docs = self._process_pdf(paper)  # Extract the PDF into chunks and append them to the doc_list.
            doc_list += docs

        """
        Embeddings are structured as follows:
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
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # Compute embeddings for each chunk and store them in the database.
        self.db_: Chroma = Chroma.from_documents(doc_list, embeddings)

    def papers(self) -> Dict[str, Paper]:
        """
        Returns the dictionary of papers.

        Returns:
            Dict[str, Paper]: A dictionary containing paper titles as keys and Paper objects as values.
        """
        return self.papers_

    def _process_pdf(self, paper: Paper) -> List[Document]:
        """
        Download a PDF, extract its content, and split it into text chunks.

        Args:
            paper (Paper): A Paper object representing the paper to be processed.

        Returns:
            List[Document]: A list of Document objects, each containing a text chunk with metadata.
        """
        # Download the PDF and obtain the file path.
        pdf_path = paper.download()
        print(f"Loading PDF: {pdf_path}")
        
        # Load the PDF content.
        loader = PyPDFLoader(pdf_path)
        pdf = loader.load()
        print(f"Extracting & splitting text from paper: {paper.title}")
        
        # Initialize a text splitter.
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        
        # Split the PDF into text chunks (list of Document objects).
        docs = text_splitter.split_documents(pdf)
        
        # Assign the same title to each chunk.
        for doc in docs:
            doc.metadata['source'] = paper.title
        
        return docs

    def retrieve(self, query: str) -> List[Document]:
        """
        Search for papers related to a query using text embeddings and cosine distance.

        Args:
            query (str): The query string to search for related papers.

        Returns:
            List[Document]: A list of Document objects representing the related papers found.
        """
        print(f'Searching for related works of: {query}...')
        sources: List[Document] = self.db_.similarity_search(query)
        source_list: List[Document] = []
        for source in sources:
            # Filter out reference sections.
            if contains_arxiv_reference(source.page_content):
                print('Skipping as this source is from the reference section...')
                continue
            source_list.append(source)
        print(f'{len(source_list)} sources found.')
        return source_list

