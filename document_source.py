# To handle the issue https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950/5
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from typing import Dict, List
import uuid
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma


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
        print(f'Initiating vectordb {db_uuid}.')
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
