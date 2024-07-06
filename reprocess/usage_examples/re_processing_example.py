from reprocess.re_processors import JsonConverter, ReContainer, GraphBuilder, CloneRepository, Compose, RegExpFinder

# Initialize a ReContainer object with the name of the repository, 
# the path where the repository will be cloned,
# and the path where the JSON graphs will be saved.
repo_container = ReContainer("arxiv-feed",
                             "/Users/elisey/AES/test_repo_folder/arxiv-feed",
                             "/Users/elisey/AES/test_repo_folder/db")

# Create a Compose object that specifies a sequence of operations
# to be performed on the repository. This sequence includes cloning 
# the repository, building a dependency graph, searching for components
# matching a regex pattern, and converting the repository data 
# to JSON format.
composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter()
])

# Execute the sequence of operations on 
# the repository container.
new_container = composition(repo_container)
