from code_dependency_grapher.cdg.repository_processors import JsonConverter, RepositoryContainer, GraphBuilder, CloneRepository, Compose, RegExpFinder

repo_container = RepositoryContainer(
    "arxiv-feed", "/Users/elisey/AES/test_repo_folder/arxiv-feed",
    "/Users/elisey/AES/test_repo_folder/db")
composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter()
])

new_container = composition(repo_container)
