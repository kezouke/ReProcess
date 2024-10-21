from reprocess.re_processors import JsonConverter, GraphBuilder, CloneRepository, Compose, RegExpFinder
from reprocess.re_container import ReContainer
import os

# Define paths using absolute paths
base_path = os.path.abspath(os.getcwd())
repo_save_path = os.path.join(base_path, "arxiv-feed")
json_save_path = os.path.join(base_path, "db")

# Initialize a ReContainer object with the repository name,
# the path where the repository will be cloned, and the path
# where the JSON graphs will be saved.
repo_container = ReContainer("arxiv-feed", repo_save_path, json_save_path)

# Create a Compose object that specifies a sequence of operations
# to be performed on the repository. This sequence includes cloning
# the repository, building a dependency graph, searching for components
# matching a regex pattern, and converting the repository data to JSON format.

composition_list = [
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter(),
]

composition = Compose(composition_list)

# Execute the sequence of operations on the repository container.
new_container = composition(repo_container)
