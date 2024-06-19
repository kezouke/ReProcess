# from code_dependency_grapher.cdg.Engine import Engine

# # Example usage
# db_abs_path = "/home/db"
# path_where_to_store_repos = "/home"
# engine = Engine(db_abs_path, path_where_to_store_repos)

# engine.clone("https://github.com/arXiv/arxiv-feed")

# engine.request(repo_folder_name="arxiv-feed")

# component = engine.componentSearch("arxiv-feed", r'\bfeed\.routes\.status\b')
# print(component.component_code)

# # Additional example requests commented out for brevity
# # engine.request("https://github.com/vllm-project/vllm")
# # engine.request("https://github.com/showpiecep/SQLite_PyQt")
# =======
# from code_dependency_grapher.cdg.Engine import Engine
# from code_dependency_grapher.cdg.JsonDeconverter import JsonDeconverter
# from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer

# # Example usage
# db_abs_path = "/home/db"
# path_where_to_store_repos = "/home"
# # engine = Engine(db_abs_path, path_where_to_store_repos)

# # engine.clone("https://github.com/arXiv/arxiv-feed")

# # engine.request(repo_folder_name="arxiv-feed")

# # component = engine.componentSearch("arxiv-feed", r'\bfeed\.routes\.status\b')
# # print(component.component_code)
# to_deconvert = RepositoryContainer("arxiv-feed", "/home/data", "", "", "/home/db")

# JsonDeconverter().deconvert(to_deconvert)

# print(to_deconvert.code_components[0])
# print(to_deconvert.files[-1])
# # Additional example requests commented out for brevity
# # engine.request("https://github.com/vllm-project/vllm")
# # engine.request("https://github.com/showpiecep/SQLite_PyQt")
# >>>>>>> b-053
# # engine.request("https://github.com/IU-Capstone-Project-2024/SayNoMore")

from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from code_dependency_grapher.cdg.repository_processors.graph_updater import GraphUpdater
from code_dependency_grapher.cdg.repository_processors.JsonConverter import JsonConverter
from code_dependency_grapher.cdg.repository_processors.JsonDeconverter import JsonDeconverter
from code_dependency_grapher.cdg.repository_processors.graph_builder import GraphBuilder

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
JsonDeconverter().process(repo_container)
GraphUpdater().process(repo_container)
# GraphBuilder().process(repo_container)
JsonConverter().process(repo_container)
