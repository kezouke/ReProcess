from code_dependency_grapher.cdg.repository_processors import GraphBuilder, JsonConverter, RepositoryContainer, Compose, CloneRepository

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
Compose(repo_container, [CloneRepository("https://github.com/arXiv/arxiv-feed"), GraphBuilder(), JsonConverter()])
