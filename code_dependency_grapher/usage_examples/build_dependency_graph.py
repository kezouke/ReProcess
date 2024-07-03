from code_dependency_grapher.cdg.repository_processors import JsonConverter, RepositoryContainer, GraphBuilder, CloneRepository, Compose
from code_dependency_grapher.utils.attribute_linker import get_attribute_linker

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    JsonConverter()
])
# aboba = CloneRepository("https://github.com/arXiv/arxiv-feed")
# new_container = aboba(repo_container)
# GraphBuilder()
# JsonConverter()
new_container = composition(repo_container)
attr_linker = get_attribute_linker()
builder = GraphBuilder()
print(builder.required_attrs)
# print(f'Old:{repo_container.code_components[0]}')
