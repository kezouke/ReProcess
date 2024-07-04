from reprocess.repository_processors import JsonConverter, ReContainer, GraphBuilder, CloneRepository, Compose, RegExpFinder

repo_container = ReContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter()
])

new_container = composition(repo_container)
