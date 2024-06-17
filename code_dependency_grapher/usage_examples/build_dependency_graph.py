from code_dependency_grapher.cdg.Engine import Engine
from code_dependency_grapher.cdg.CodeComponent import CodeComponent

# Example usage
db_abs_path = "/home/db"
path_where_to_store_repos = "/home/repos/"
engine = Engine(db_abs_path, path_where_to_store_repos)

component = engine.componentSearch("arxiv-feed", r'\bfeed\.routes\.status\b')
print(component.component_code)

engine.clone("https://github.com/arXiv/arxiv-feed")

engine.request("https://github.com/arXiv/arxiv-feed")

# Additional example requests commented out for brevity
# engine.request("https://github.com/vllm-project/vllm")
# engine.request("https://github.com/showpiecep/SQLite_PyQt")
# engine.request("https://github.com/IU-Capstone-Project-2024/SayNoMore")
