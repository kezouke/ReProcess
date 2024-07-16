# ReProcess
_release version: 0.2_

----

ReProcess (`Re` stands for `Repository`) is an open-source system designed for the easy processing and analyzing of Git Python repositories.

----


## Features

ReProcess provides several key features:
- **Dependency Tree Generation**: Build a dependency tree of all components (class, class method, or function) within a repository, showing how these components are related.
- **Dependency Tree Update**: Update an existing Git repository's dependency tree when changes are made to the code after an initial tree is built.
- **Component Search**: Quickly find code components whose names match a given regular expression (default is `r "*"`).
- **Data Persistence**: Save and read built trees, found components, and other repository data attributes to/from JSON.

Users can use local folders with their repositories or use the `CloneRepository` predefined ReProcessor to download the repository.

Currently, ReProcess supports Git repositories and Python files. Users can also write their own custom repository handlers using the full functionality of ReProcess.

## Installation

### Step 1: Clone the Repository
Begin by cloning the ReProcess repository to your local machine.
```bash
git clone https://github.com/kezouke/TestGena
```

### Step 2: Navigate to the Project Directory
Change the directory to enter the project folder.
```bash
cd TestGena
```

### Step 3: Install the Library
Execute the `setup.py` script to install the `reprocess` library.
```bash
python3 -m pip install -e .
```

These steps will set up the necessary environment for using the library in your local development environment.

## Usage

### Running the ReProcess Example Script
To execute the usage example script of our library, use the following command:
```bash
python -m reprocess.usage_examples.re_processing_example 
```

This script demonstrates how to utilize the ReProcess library.

### Example Usage Script
```python
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
```

### Description of ReContainer
The `ReContainer` (`Re` stands for `Repository`) is the main class for handling repositories within ReProcess. This class stores any attributes related to the repository that the user is processing, such as the hash of the last commit, all `.py` files in the repository, etc. The `ReContainer` is central to the processing of repositories. The set of attributes that an `ReContainer` instance can store is flexible and dynamic; each repository handler can expect and create attributes as needed, making the `ReContainer` highly adaptable to different processing requirements.

### Parameters of the ReContainer
- **repo_name**: Name of the repository.
- **repo_path**: Directory where the repository will be cloned.
- **db_path**: Directory where the JSON graphs will be saved.

Note that each individual `ReProcessor` is capable of adding new attributes to the container instance, so the above parameters are not the only ones. They are defined by the `ReProcessor` that has been applied to the `ReContainer`.


### List of ReProcessors
- **CloneRepository**: Clones a repository from a given Git URL.
  ```python
  Compose(repo_container, [CloneRepository("https://github.com/arXiv/arxiv-feed")])
  ```

- **GraphBuilder**: Builds a graph of the repository and saves it into the specified `db_path`. It also populates the repository container.
  ```python
  Compose(repo_container, [GraphBuilder()])
  ```

- **GraphUpdater**: Updates the graph of the repository and updates the `json` file accordingly, refining the repository container.
  ```python
  Compose(repo_container, [GraphUpdater()])
  ```

- **JsonConverter**: Converts fields of the repository container into a `json` file, placed according to the specified `db_path`.
  ```python
  Compose(repo_container, [JsonConverter()])
  ```

- **JsonDeconverter**: Converts `json` from the `repository_container.db_path` field and populates all attributes of the repository container.
  ```python
  Compose(repo_container, [JsonDeconverter()])
  ```

- **RegExpFinder**: Searches components by regular expression for the name and saves all found `CodeComponent`s in the repository container.
  ```python
  Compose(repo_container, [RegExpFinder(r'\bfeed\.routes\.status\b')])
  ```
  This processor will update `repo_container` by adding a new attribute with the same name as the passed regular expression and will store all found    code components satisfying that regular expression.

- **LocalLoader**: Loads local repository and checks if given path to the repo exists.
  ```python
    Compose(repo_container, [LocalLoader()])
    ```
- **Compose**: Executes a sequence of other processors on the repository container.
  ```python
  Compose(repo_container, [Processors_list])
  new_container = composition(repo_container)
  ```

This set of processors allows flexible management and analysis of code dependencies within repositories.

## Creating Custom Repository Processors

Users can create their own repository processors by making classes that inherit from `ReProcessor`. When creating a custom processor, the class should:

1. **Inherit from `ReProcessor`**: This ensures that the necessary checks and behaviors are inherited.
2. **Implement the `__call__` Method**: This method should accept a `ReContainer` instance as an argument and return a dictionary with updated attributes and their values. The `ReContainer` should not be explicitly modified within the `__call__` method.

### Example Code for a Custom Repository Processor
```python
# Import necessary classes and exceptions from the reprocess package
from reprocess.re_processors.processor import ReProcessor
from reprocess.repository_container import ReContainer
from reprocess.re_processors import Compose


# Define a custom ReProcessorA class that extends the ReProcessor class
class ReProcessorA(ReProcessor):

    def __call__(self, repository_container: ReContainer):
        # Return a dictionary with the attribute 'attr_a' set to 10
        return {"attr_a": 10}

# Create an example repository container with specific paths
re_container_example = ReContainer("test_1", "/test_1", "/db")

# Instantiate the custom ReProcessors
a = ReProcessorA()

# Create a composition with both ReProcessorA
composition_example = Compose([a])

# Run the composition to process the repository container
new_container = composition_example(re_container_example)

# Print the attributes of the new container
print(new_container.__dict__)
'''
Expected output:
{'repo_name': 'test_1',
 'repo_path': '/test_1', 
 'db_path': '/db', 
 'attr_a': 10
}
'''
```

This script showcases how to define and compose custom processor. If you want to dive into the intricacies of creating and working with custom processors, we advise you to run the usage example `creating_custom_re_processor.py`:

```bash
python3 -m reprocess.usage_examples.creating_custom_re_processor
```

This demonstrates the flexibility of creating and using custom processors within the ReProcess library.

### Handling Incorrect Usage

If the `ReContainer` is used or changed in an incorrect manner, the user will be guided automatically on how to resolve the issue. This is done through the `AbsentAttributesException` and internal checks that ensure required attributes are present and the container is not modified explicitly.

## JSON Tree Structure Description

The JSON structure generated by ReProcess can have an arbitrary structure. The exact format depends on the ReProcessors that have been executed before running the JsonConverter. The JsonConverter stores every attribute in the ReContainer, including nested ones, making the JSON output highly flexible and tailored to the specific processing performed on the repository.

The example below is obtained after running the ReProcessors sequence of `CloneRepository`, `GraphBuilder`, and `JsonConverter`.

#### Top-Level Structure
- `files`: A list of dictionaries, each representing a file analyzed.
- `code_components`: A list of dictionaries, each representing a component (function, class, or method) identified within the files.
- `external_components`: A list of IDs of external import statements (components outside the parsed repo).

#### `files` List
Each dictionary in the `files` list contains:
- `file_id`: A unique identifier for the file.
- `file_path`: The relative path to the file.
- `imports`: A list of strings representing all imported modules and components in the file.
- `called_components`: A list of strings representing all components or functions called within the file.
- `callable_components`: A list of strings representing all functions or classes defined in the file that can be called.

#### `code_components` List
Each dictionary in the `components` list contains:
- `component_id`: A unique identifier for the component.
- `component_name`: The full name of the component, including its module or file context.
- `component_code`: The actual code of the component.
- `linked_component_ids`: A list of component IDs representing other components that are linked or associated with this component.
- `file_id`: The ID of the file that processed this component.
- `external_component_ids`: A list of IDs representing external components that this component interacts with.
- `component_type`: One of 3 possible types of components ("class", "method", or "function").

This structure helps in understanding the relationships and dependencies among various files and components in the project.

### Real Example of the JSON
```json
{
    "external_components": {
        "71507f0f-0ead-4018-a8cb-d3b864ea4d8d": "flask.make_response",
        "c1327f0a-b679-4c91-aa98-e4ccd2ed4b73": "flask.current_app",
        "782625df-3b8b-4cee-b489-ac154218837d": "werkzeug.Response"
    },
    "code_components": [
        {
            "component_id": "7eea4ee61fd779eb579e3ace87edf1f2156793a2c43f0f4699fb6ed3bdefea04",
            "component_name": "feed.routes.status",
            "component_code": "from feed.database import check_service\nfrom flask import make_response, current_app\nfrom werkzeug import Response\n\n@blueprint.route('/feed/status')\ndef status() -> Response:\n    text = f\"Status: {check_service()} Version: {current_app.config['VERSION']}\"\n    return make_response(text, 200)",
            "linked_component_ids": [
                "d36fb25e1f23eb276f18656eead6360ae963d573e0304361a4ee608831e2ae69"
            ],
            "file_id": "bb2bd632-a392-429d-9b04-fc6e70fd5875",
            "external_component_ids": [
                "71507f0f-0ead-4018-a8cb-d3b864ea4d8d",
                "c1327f0a-b679-4c91-aa98-e4ccd2ed4b73",
                "782625df-3b8b-4cee-b489-ac154218837d"
            ],
            "component_type": "function",
            "__class__": "CodeComponentContainer"
        }
    ],
    "files": [
        {
            "file_id": "03ea4512-375c-457e-b8c9-a53f70c0c1c5",
            "file_path": "feed/serializers/extensions.py",
            "imports": [
                "Dict",
                "List",
                "Optional",
                "etree",
                "Element",
                "BaseEntryExtension",
                "BaseExtension",
                "Author"
            ],
            "called_components": [
                "SubElement",
                "__add_authors",
                "join"
            ],
            "callable_components": [
                "ArxivAtomExtension",
                "ArxivExtension",
                "ArxivEntryExtension"
            ],
            "__class__": "FileContainer"
        }
    ],
    "repo_author": "78058179+kyokukou@users.noreply.github.com",
    "repo_hash": "3720f2018d8e59b6c760de53f515e7eda0ed16c7",
    "repo_name": "arxiv-feed",
    "repo_path": "/home/arxiv-feed",
    "db_path": "/home/db"
}
```
