from paper_class import Paper
from datetime import datetime


def get_test_papers():
    papers = {
        "paper 1": Paper(
            title="paper 1",
            summary="",
            authors=["Xiang Li", ", Yiqun Yao"],
            url="https://arxiv.org/pdf/2309.00240",
            publish_date=datetime.strptime("2020", "%Y"),
        ),
        "paper 2": Paper(
            title="paper 2",
            summary="",
            authors=["Xin Jiang", "Xuezhi Fang"],
            url="https://arxiv.org/pdf/2309.00087",
            publish_date=datetime.strptime("2020", "%Y"),
        ),
    }

    return papers
