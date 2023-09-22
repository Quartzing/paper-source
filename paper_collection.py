import os
import arxiv
from paper_class import Paper


class PaperCollection(object):
    def __init__(self):
        self.papers = {}

    def add_paper(self, paper: Paper):
        self.papers[paper.title] = paper

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
            self.papers[paper.title] = paper
            if download:
                paper.download(use_title=True)
        

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

    for title, paper in paper_collection.papers.items():
        print(paper.get_arxiv_citation())
        print(paper.get_APA_citation())
