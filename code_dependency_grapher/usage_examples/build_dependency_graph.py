# from code_dependency_grapher.cdg.Engine import Engine

# # Example usage
# db_abs_path = "/home/db"
# path_where_to_store_repos = "/home"
# engine = Engine(db_abs_path, path_where_to_store_repos)

# engine.clone("https://github.com/arXiv/arxiv-feed")

# engine.request(repo_folder_name="arxiv-feed")

# component = engine.componentSearch("arxiv-feed", r'\bfeed\.routes\.status\b')
# print(component.component_code)

# # # Additional example requests commented out for brevity
# # # engine.request("https://github.com/vllm-project/vllm")
# # # engine.request("https://github.com/showpiecep/SQLite_PyQt")
# # =======

from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from code_dependency_grapher.cdg.repository_processors.graph_updater import GraphUpdater
from code_dependency_grapher.cdg.JsonDeconverter import JsonDeconverter


repo_container = RepositoryContainer("arxiv-feed", 
                                     "/home/arxiv-feed",
                                     "",
                                     "",
                                     "/home/db")

JsonDeconverter().deconvert(repo_container)

GraphUpdater().process(repo_container)
# for cmp in repo_container.code_components:
#     print(cmp.component_id)
#     print(cmp.linked_component_ids)
#     print(cmp.component_name)
