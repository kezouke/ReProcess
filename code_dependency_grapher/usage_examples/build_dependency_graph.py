from code_dependency_grapher.cdg.repository_processors import JsonDeconverter, GraphUpdater, JsonConverter, RepositoryContainer, Compose, GraphBuilder, CloneRepository

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
new_container = Compose(repo_container, [
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    JsonConverter()
])
