from paper_source import PaperSource


class PaperContentSource(PaperSource):
    def __init__(self, 
                 papers: Dict[str, Paper], 
                 openai_api_key: str,
                 ignore_references: bool = True):
        """
        Initializes with a dictionary of papers and an OpenAI API key.

        Args:
            papers (Dict[str, Paper]): A dictionary containing paper titles as keys and object of class Paper as values.
            openai_api_key (str): The OpenAI API key for text embeddings.
            ignore_references (bool): Whether to ignore the chunks containing references.
        """
        # The ignore references member var should be defined first as we are using it when calling the base class constructor.
        self.ignore_references_ = ignore_references
        super().__init__(
            papers=papers,
            openai_api_key=openai_api_key,
        )

    def _process_paper(self, paper: Paper) -> List[Document]:
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


if __name__ == '__main__':
    paper_content_source = PaperContentSource()
