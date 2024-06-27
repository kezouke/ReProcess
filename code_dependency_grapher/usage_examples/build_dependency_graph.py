from code_dependency_grapher.cdg.repository_processors import JsonConverter, RepositoryContainer, Compose, GraphBuilder, CloneRepository

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    JsonConverter()
])

new_container = composition(repo_container)
