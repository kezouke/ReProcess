from code_dependency_grapher.cdg.repository_processors import JsonConverter, RepositoryContainer, Compose, GraphBuilder, CloneRepository, JsonDeconverter

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
new_container = Compose(repo_container, [
    JsonDeconverter(),
    GraphBuilder(),
    JsonConverter()
])
