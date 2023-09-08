import openai
import os
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from tools import *


class PaperSource(object):
    def __init__(self, papers: dict, openai_api_key: str):
        '''Given a url dict(title: url) and chat with it.
        args:
          papers: dict
            title: key
            url: value
          openai_api_key: str
        '''
        self.papers_ = papers
        doc_list = []
        for title, paper in papers.items():
            docs = self._process_pdf(paper) # extract the pdf into chuncks and then put it into docs(list)
            doc_list += docs # push in different paper

        '''Embeddings are like following:
        ['embedding':page_info,
          '[122143,123213,346346,34325234]':{page_content = 'LLM XXX',
                                            metadata = {
                                              source = 'title ',
                                              pege = int,
                                            },}]
        '''
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # every chunck compute the embedding and store to the data base
        self.db_ = Chroma.from_documents(doc_list, embeddings)

    def papers(self):
        return self.papers_

    def _process_pdf(self, paper):
        '''download pdf and read the PDF and extra to the txt'''
        # download pdf and return file name
        pdf_path = paper.download()
        print(f"Loading pdf {pdf_path}")
        # read the pdf
        loader = PyPDFLoader(pdf_path)
        pdf = loader.load()
        print(f"Extracting & splitting text from paper: {paper.title}")
        # initialize text_splitter
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        # split the pdf into text chuncks(list)
        docs = text_splitter.split_documents(pdf)
        # give different chunck the same title
        for doc in docs:
            doc.metadata['source'] = paper.title
        return docs

    def retrieve(self, query: str) -> list:
        '''compute the embeding of input qurey and find the similar ones in docs list with cosine distance
        Returns:
          sources: a list of value, sources = [{page_content = 'LLM XXX',
                    metadata = {
                        source = 'title ',
                        pege = int},
                  }]
        '''
        print(f'Searching for the related works of {query}...')
        sources: list = self.db_.similarity_search(query)
        source_list = []
        for source in sources:
            # Filter the reference sections
            if contains_arxiv_reference(source.page_content):
                print('Skipping as this source is from reference section...')
                continue
            source_list.append(source)
        print(f'{len(source_list)} sources found.')
        return source_list
