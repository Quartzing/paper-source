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


class DocumentSource:
    def __init__(self, 
                 documents: list[Document], 
                 openai_api_key: str):
        """
        Initializes with a dictionary of papers and an OpenAI API key.

        Args:
            papers (list[Document]): A list containing documents.
            openai_api_key (str): The OpenAI API key for text embeddings.

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
        # Get embedding from OpenAI.
        embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # UUID4: Generates a random UUID in UUID class type.
        db_uuid = str(uuid.uuid4())
        # Compute embeddings for each chunk and store them in the database. Each with a unique id to avoid conflicts.
        print(f'Initiating vectordb {db_uuid} with {len(doc_list)} documents from {len(self.papers_)} papers.')
        self.db_: Chroma = Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            collection_name=db_uuid,
        )

    def retrieve(self, query: str, num_retrieval: int | None =None) -> List[Document]:
        """
        Search for documents related to a query using text embeddings and cosine distance.

        Args:
            query (str): The query string to search for related documents.

        Returns:
            List[Document]: A list of Document objects representing the related documents found.
        """
        print(f'Searching for related works of: {query}...')
        if not num_retrieval:
            num_retrieval = len(self.papers_)
        sources: List[Document] = self.db_.similarity_search(query, k=num_retrieval)
        print(f'{len(sources)} sources found.')
        return sources


class PaperSource:
    def __init__(self, 
                 papers: Dict[str, Paper], 
                 openai_api_key: str,
                 ignore_references: bool = True):
        """
        Initializes a PaperSource object with a dictionary of papers and an OpenAI API key.

        Args:
            papers (Dict[str, Paper]): A dictionary containing paper titles as keys and object of class Paper as values.
            openai_api_key (str): The OpenAI API key for text embeddings.
            ignore_references (bool): Whether to ignore the chunks containing references.
        """
        self.ignore_references_ = ignore_references
        self.papers_: Dict[str, Paper] = papers
        doc_list: List[Document] = []
        for title, paper in papers.items():
            docs = self._process_pdf(paper)  # Extract the PDF into chunks and append them to the doc_list.
            doc_list += docs
            
        self.document_source_ = DocumentSource(
            documents=doc_list,
            openai_api_key=openai_api_key,
        )

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
        doc_list = []
        for doc in docs:
            # Filter out reference sections if choose to ignore them.
            if self.ignore_references_ and contains_arxiv_reference(doc.page_content):
                print('The reference section is skipped.')
                continue
            doc.metadata['source'] = paper.title
            doc_list.append(doc)
        
        return doc_list

    def retrieve(self, **kwargs) -> List[Document]:
        """
        Search for papers related to a query using text embeddings and cosine distance.

        Args:
            query (str): The query string to search for related papers.

        Returns:
            List[Document]: A list of Document objects representing the related papers found.
        """
        return self.document_source_.retrieve(**kwargs)
    

if __name__ == '__main__':
    from test_utils import get_test_papers
    
    paper_source = PaperSource(
        papers=get_test_papers(),
        openai_api_key='',
        ignore_references=True,
    )
    
    print(paper_source.retrieve(query='test', num_retrieval=5))
