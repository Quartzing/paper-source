from paper_class import Paper


class PaperCollection(object):
    def __init__(self,
                 paper_summary_source: PaperSummarySource):
        self.paper_summary_source_ = paper_summary_source

    def add_paper(self, paper: Paper):
        self.paper_summary_source_.add_paper(paper)

    def add_from_arxiv(self,
                       search,
                       download: bool = False):
        """
        Search for papers on arXiv and optionally download them.
    
        Args:
            search: A container of arXiv search results.
    
        """
        output_directory: str = "arxiv_papers"
        os.makedirs(output_directory, exist_ok=True)
    
        for result in search.results():
            paper: Paper = Paper(title=result.title,
                          summary=result.summary,
                          url=result.pdf_url,
                          authors=[author.name for author in result.authors],
                          publish_date=result.published)
            self.add_paper(paper)
            if download:
                paper.download(use_title=True)
    
    def get_all_papers(self) -> dict[Paper]:
        '''Get all papers.'''
        return self.paper_summary_source_.papers()

    def get_paper(self, title: str) -> Paper:
        return get_all_papers()[title]

    def get_papers_of_topic(self, query: str, num_retrieval: int = 5) -> dict[str, Paper]:
        print(f"Collecting papers with topic {query}...")
        paper_set = set()
        sources: List[Paper] = self.paper_summary_source_.retrieve(
            query=query,
            num_retrieval=num_retrieval,
        )

        for source in sources:
            title = source.metadata['source']
            paper_set.add(title)

        paper_dict = {title: self.get_paper(title) for title in paper_set}

        print(f"{len(paper_dict)} papers found.")

        return paper_dict
        

if __name__ == '__main__':
    search = arxiv.Search(
        query = "au:Yanrui Du AND ti:LLM",
        max_results = 3,
        sort_by = arxiv.SortCriterion.SubmittedDate,
        sort_order = arxiv.SortOrder.Descending
    )

    paper_collection = PaperCollection()

    paper_collection.add_from_arxiv(
        search,
        download=False,
    )

    for title, paper in paper_collection.get_all_papers().items():
        print(paper.get_arxiv_citation())
        print(paper.get_APA_citation())

    for title, paper in paper_collection.get_papers_of_topic("Yanrui").items():
        print(paper.get_arxiv_citation())
        print(paper.get_APA_citation())
