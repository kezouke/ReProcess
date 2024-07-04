from reprocess.repository_processors import JsonConverter, RepositoryContainer, GraphBuilder, CloneRepository, Compose, RegExpFinder

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter()
])

new_container = composition(repo_container)
