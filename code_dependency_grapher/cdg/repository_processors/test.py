from code_dependency_grapher.cdg.repository_processors import CloneRepository, RepositoryContainer, GraphUpdater
from code_dependency_grapher.utils.attribute_linker import get_attribute_linker


repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")

aboba = CloneRepository("https://github.com/arXiv/arxiv-feed", inplace=False)
babam = GraphUpdater()
# print(aboba.inplace)
new_repcon = babam(repo_container)
# print(aboba.required_attrs)
attr_linker = get_attribute_linker()

# print(attr_linker.attrs_to_classf)