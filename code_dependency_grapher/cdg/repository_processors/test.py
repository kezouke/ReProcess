from code_dependency_grapher.cdg.repository_processors import CloneRepository, RepositoryContainer

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")


aboba = CloneRepository("https://github.com/arXiv/arxiv-feed", inplace=False)
# print(aboba.inplace)
new_repcon = aboba(repo_container)
print(id(repo_container))
print(id(new_repcon))