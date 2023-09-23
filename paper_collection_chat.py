import openai
from langchain.docstore.document import Document
from paper_source import PaperSource
from paper_class import Paper
from paper_collection import PaperCollection
from agents import Researcher
from typing import List, Tuple


class PaperCollectionChat(object):
    def __init__(self,
                 paper_collection: PaperCollection,
                 openai_api_key: str,
                 ignore_references: bool = True):
        """
        Initialize a PaperChat instance.

        Args:
            paper_source (PaperSource): A PaperSource object providing access to research papers.
        """
        self.paper_collection_ = paper_collection
        self.paper_source_ = functools.partial(PaperSource(
            openai_api_key=openai_api_key,
            ignore_references=ignore_references,
        ))

    def _source(self, **kwargs) -> list[(Document, int)]:
        """
        Perform a query and provide an answer along with the relevant sources.

        Args:
            **kwargs (dict): The args used by retrieve function of DocumentSource class.

        Returns:
            list of tuple: A list of tuple containing the answer generated based on the qfuery
                and a list of relevant source papers and the relevance score.
        """
        papers: dict[str, Paper] = self.paper_collection_.query_papers(**kwargs)
        paper_source: PaperSource = self.paper_source_(papers=papers)

        return paper_source.retrieve(**kwargs)
        

    def query(self, **kwargs) -> Tuple[str, List[str]]:
        """
        Perform a query and provide an answer along with the relevant sources.

        Args:
            **kwargs (dict): The args used by retrieve function of DocumentSource class.

        Returns:
            tuple: A tuple containing the answer generated based on the query and a list of relevant source papers.
        """
        user_query = kwargs['query']
        print(f'Querying {user_query}')

        sources: List[(Document, int)] = self._source(**kwargs)
        user_input: str = f"{user_query} with the following paper contents as context for your reference:\n"
        for source, score in sources:
            user_input += f"{source}\n"

        researcher: Researcher = Researcher(model='gpt-3.5-turbo-16k')
        answer: str = researcher.query(user_input)  # Use this input to get the response
        print('Answer: ', answer)
        print('Sources: ', sources)
        return answer, sources

    def source_and_summarize(self, **kwargs) -> List[(Document, int)]:
        """
        Find and summarize related works for a user query based on the given paper pool.

        Args:
            **kwargs (dict): The args used by retrieve function of DocumentSource class.

        Returns:
            list of tuple: A list of tuple containing Document objects with added summary information
                and relevance score.
        """
        user_query = kwargs['query']
        print(f'Finding related works for {user_query}...')
        sources: List[(Document, int)] = self._source(**kwargs)
        if len(sources) == 0:
            raise ValueError('No sources found.')
        agent: Researcher = Researcher(model='gpt-3.5-turbo')
        for source, score in sources:
            user_input: str = f"Summarize the following paper contents with exactly ONE concise sentence for how it relates to {user_query}, " \
                             f"output it in the format of 'XXXXXXX (A Question/Method/Model/Concept/Results/Conclusion etc.) was proposed/raised/mentioned/analyzed/found " \
                             f"that XXXXX': {source.page_content}\nPlease do not mention 'this paper' or 'figure' or 'table' in the summary."
            summary: str = agent.query(user_input)
            print(summary)
            source.metadata['summary'] = summary  # Assuming you want to store the summary in source metadata
            source.metadata['score'] = score
        return sources


if __name__ == '__main__':
    from test_utils import get_test_papers
    import os

    openai.api_key = os.getenv('OPENAI_API_KEY')

    paper_collection = PaperCollection(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        chunk_size=1000,
    )
    
    paper_collection.add_paper_dict(get_test_papers())

    chat = PaperCollectionChat(
        paper_collection=paper_collection,
        openai_api_key=openai.api_key,
        ignore_references=True,
    )
    prompt = ''''Medical Scene - Text-Only Modality - Medical Q&A (Specialized Knowledge).'''
    sources = chat.source_and_summarize(
        query=prompt,
        score_threshold=0.4,
    )
