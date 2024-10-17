from reprocess.re_processors import JsonConverter, GraphBuilder, CloneRepository, Compose, RegExpFinder, Neo4jConverter
from reprocess.re_container import ReContainer

# Initialize a ReContainer object with the name of the repository,
# the path where the repository will be cloned,
# and the path where the JSON graphs will be saved.
repo_container = ReContainer("arxiv-feed", "/home/arxiv-feed", "/home/db")

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7299"  # URI for the Neo4j database
NEO4J_USERNAME = "neo4j"  # Username for Neo4j login
NEO4J_PASSWORD = "password"  # Password for Neo4j login

# Create a Compose object that specifies a sequence of operations
# to be performed on the repository. This sequence includes cloning
# the repository, building a dependency graph, searching for components
# matching a regex pattern, and converting the repository data
# to JSON format,  and integrating the repository data with Neo4j
# for graph storage and querying.
composition = Compose([
    CloneRepository(),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter(),
    Neo4jConverter(NEO4J_URI, NEO4J_USERNAME,
                   NEO4J_PASSWORD)  # Store the graph data in Neo4j
])
# Execute the sequence of operations on
# the repository container.
new_container = composition(repo_container)
