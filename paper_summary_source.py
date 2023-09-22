from paper_source import PaperSource


class PaperSummarySource(PaperSource):
    def __init__(self, 
                 papers: Dict[str, Paper], 
                 openai_api_key: str,
                 chunk_size: int = 2000):
        """
        Initializes with a dictionary of papers and an OpenAI API key.

        Args:
            papers (Dict[str, Paper]): A dictionary containing paper titles as keys and object of class Paper as values.
            openai_api_key (str): The OpenAI API key for text embeddings.
            chunk_size (int): The size of the chunk to splitting the summary (abstract).
        """
        # The chunk_size_ member var should be defined first as we are using it when calling the base class constructor.
        self.chunk_size_ = chunk_size
        super().__init__(
            papers=papers,
            openai_api_key=openai_api_key,
        )

    def _process_paper(self, paper: Paper) -> List[Document]:
        """
        Split the paper summary into text chunks.

        Args:
            paper (Paper): A Paper object representing the paper to be processed.

        Returns:
            List[Document]: A list of Document objects, each containing its summary (abstract).
        """
        # Initialize a text splitter.
        text_splitter = CharacterTextSplitter(chunk_size=self.chunk_size_, chunk_overlap=0)
        
        docs = text_splitter.create_documents([paper.summary])
        for doc in docs:
            doc.metadata['source'] = paper.title

        return docs
