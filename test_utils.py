def get_test_papers():
    papers = {
        "paper 1": Paper(
            title="paper 1",
            summary="",
            authors=[],
            url="https://arxiv.org/pdf/2309.00240",
            publish_date=datetime.strptime("2020", "%Y"),
        ),
        "paper 2": Paper(
            title="paper 2",
            summary="",
            authors=[],
            url="https://arxiv.org/pdf/2309.00087",
            publish_date=datetime.strptime("2020", "%Y"),
        ),
    }

    return papers
