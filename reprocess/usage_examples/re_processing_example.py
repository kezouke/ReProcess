from reprocess.re_processors import JsonConverter, GraphBuilder, CloneRepository, Compose, RegExpFinder, Neo4jConverter
from reprocess.re_container import ReContainer
import os

# Initialize a ReContainer object with the name of the repository,
# the path where the repository will be cloned,
# and the path where the JSON graphs will be saved.

print(
    "Hello! We are about to run ReProcess on the 'arxiv-feed' repository. This will involve cloning the repository to your local machine."
)
print(
    "Could you please provide the folder path where you'd like the repository to be cloned?"
)
repo_save_path = os.path.join(input(), "arxiv-feed")
print(
    "We'll also generate and save a JSON file containing the processing results of the 'arxiv-feed' repository."
)
print(
    "Could you please specify the path where you'd like the JSON file to be saved?"
)
json_save_path = input()
repo_container = ReContainer("arxiv-feed", repo_save_path, json_save_path)

# Neo4j connection details
print("Please, enter neo4j URI (press enter if you dont need it): ")
NEO4J_URI = input()  # URI for the Neo4j database

NEO4J_USERNAME, NEO4J_PASSWORD = None, None
if NEO4J_URI:
    print("Please, enter neo4j username: ")
    NEO4J_USERNAME = input()  # Username for Neo4j login
    print("Please, enter neo4j password: ")
    NEO4J_PASSWORD = input()  # Password for Neo4j login

# Create a Compose object that specifies a sequence of operations
# to be performed on the repository. This sequence includes cloning
# the repository, building a dependency graph, searching for components
# matching a regex pattern, and converting the repository data
# to JSON format,  and integrating the repository data with Neo4j
# for graph storage and querying.

composition_list = [
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter(),
]

if NEO4J_URI:
    # Store the graph data in Neo4j
    composition_list.append(
        Neo4jConverter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD))

composition = Compose(composition_list)

# Execute the sequence of operations on
# the repository container.
new_container = composition(repo_container)
