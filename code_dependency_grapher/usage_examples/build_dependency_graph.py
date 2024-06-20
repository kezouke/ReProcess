from code_dependency_grapher.cdg.repository_processors import *

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
Compose(repo_container, [JsonDeconverter(), GraphUpdater(), JsonConverter()])
