# ReProcess README

## Release Version 
# `0.2`

## Introduction
ReProcess is a tool designed to manage dependencies within code repositories. This document provides instructions on how to set up and use the current version of ReProcess.

## Installation Steps
1. **Clone the Repository**: Begin by cloning the ReProcess repository to your local machine.

   ```bash
   git clone https://github.com/kezouke/TestGena
   ```

2. **Navigate to the Project Directory**: Change directory to enter the project folder.

   ```bash
   cd TestGena
   ```

3. **Install the Library**: Execute the setup.py script to install the `reprocess` library.

   ```bash
   python3 -m pip install -e .
   ```

These steps will set up the necessary environment for using the library in your local development environment.

## Usage

### Running the ReProcess Example Script
To execute the usage example script of our library, use the following command:

```bash
python -m reprocess.usage_examples.build_dependency_graph
```

This script demonstrates how to utilize the ReProcess library.

### Example Usage Script
```python
from code_dependency_grapher.cdg.repository_processors import JsonConverter, RepositoryContainer, GraphBuilder, CloneRepository, Compose, RegExpFinder

repo_container = RepositoryContainer(
    "arxiv-feed", "/home/test_repo_folder/arxiv-feed",
    "/home/test_repo_folder/db")

composition = Compose([
    CloneRepository("https://github.com/arXiv/arxiv-feed"),
    GraphBuilder(),
    RegExpFinder("^(.*test.*)$|^((?:.*[Tt]est).*)$"),
    JsonConverter()
])

new_container = composition(repo_container)

```

### Parameters of the Repository Container
- **repo_name**: Name of the repository.
- **repo_path**: Directory where the repository will be cloned.
- **db_path**: Directory where the JSON graphs will be saved.

### List of Repository Processors:
- **CloneRepository**: Clones a repository from a given Git URL.
  **Example**: 
  ```python
  Compose(repo_container, [CloneRepository("https://github.com/arXiv/arxiv-feed")])
  ```

- **GraphBuilder**: Builds a graph of the repository and saves it into the specified `db_path`. It also populates the repository container.
  **Example**: 
  ```python
  Compose(repo_container, [GraphBuilder()])
  ```

- **GraphUpdater**: Updates the graph of the repository and updates the `json` file accordingly, refining the repository container.
  **Example**: 
  ```python
  Compose(repo_container, [GraphUpdater()])
  ```

- **JsonConverter**: Converts fields of the repository container into a `json` file, placed according to the specified `db_path`.
  **Example**: 
  ```python
  Compose(repo_container, [JsonConverter()])
  ```

- **JsonDeconverter**: Converts `json` from the `repository_container.db_path` field and populates all attributes of the repository container.
  **Example**: 
  ```python
  Compose(repo_container, [JsonDeconverter()])
  ```

- **RegExpFinder**: Searches components by regular expression for the name and saves all found `CodeComponent`s in the repostory container.
  **Example**: 
  ```python
  Compose(repo_container, [RegExpFinder(r'\bfeed\.routes\.status\b')])
  ```

- **Compose**: Executes a sequence of other processors on the repository container.
  **Example**: 
  ```python
  Compose(repo_container, [Processors_list])
  new_container = composition(repo_container)
  ```
  
This set of processors allows flexible management and analysis of code dependencies within repositories.

## Creating Custom Repository Processors

Users can create their own repository processors by making classes that inherit from `RepositoryProcessor`. When creating a custom processor, the class should:

1. **Inherit from `RepositoryProcessor`**: This ensures that the necessary checks and behaviors are inherited.

2. **Implement the `__call__` Method**: This method should accept a `RepositoryContainer` instance as an argument and return a dictionary with updated attributes and their values. The `RepositoryContainer` should not be explicitly modified within the `__call__` method.

### Example Code for a Custom Repository Processor

```python
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from code_dependency_grapher.utils.attribute_linker import get_attribute_linker
from abc import ABC, abstractmethod, ABCMeta
import ast
import inspect
import functools
import copy

class CustomProcessor(RepositoryProcessor):
    def __call__(self, repository_container: RepositoryContainer):
        # Your processing logic here
        code_components = repository_container.code_components # you can still access any attributes you want 
        updated_attributes = {
            'new_attribute': 'new_value'
        }
        return updated_attributes
```

### Handling Incorrect Usage

If the `RepositoryContainer` is used or changed in an incorrect manner, the user will be guided automatically on how to resolve the issue. This is done through the `AbsentAttributesException` and internal checks that ensure required attributes are present and the container is not modified explicitly.

### JSON Tree Structure Description

After running the analysis, the JSON structure stored at `db_url` will have the following format:

#### Top-Level Structure:
- `files`: A list of dictionaries, each representing a file analyzed.
- `code_components`: A list of dictionaries, each representing a component (function or class or method) identified within the files.
- `external_components`: A list of ids of external import statements (components outside the parsed repo)

#### `files` List:
Each dictionary in the `files` list contains:
- `file_id`: A unique identifier for the file.
- `file_path`: The relative path to the file.
- `imports`: A list of strings representing all imported modules and components in the file.
- `called_components`: A list of strings representing all components or functions called within the file.
- `callable_components`: A list of strings representing all functions or classes defined in the file that can be called.

#### `code_components` List:
Each dictionary in the `components` list contains:
- `component_id`: A unique identifier for the component.
- `component_name`: The full name of the component, including its module or file context.
- `component_code`: The actual code of the component.
- `linked_component_ids`: A list of component IDs representing other components that are linked or associated with this component.
- `file_id`: The ID of the file  that processed this component.
- `external_component_ids`: A list of IDs representing external components that this component interacts with.
- `component_type`: One of 3 possible types of component ("class", "method" or "function")

This structure helps in understanding the relationships and dependencies among various files and components in the project.

### Real Example of the json:
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
        },
    ],
    "repo_author": "78058179+kyokukou@users.noreply.github.com",
    "repo_hash": "3720f2018d8e59b6c760de53f515e7eda0ed16c7",
    "repo_name": "arxiv-feed",
    "repo_path": "/home/arxiv-feed",
    "db_path": "/home/db"
}
```
