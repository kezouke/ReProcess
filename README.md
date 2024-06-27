# Code Dependency Grapher README

## Release Verison 
#`0.1`

## Introduction
The Code Dependency Grapher is a tool designed to manage dependencies within code repositories. This document provides instructions on how to set up and use the current version of the Code Dependency Grapher.

## Installation Steps
1. **Clone the Repository**: Begin by cloning the Code Dependency Grapher repository to your local machine.

   ```bash
   git clone https://github.com/kezouke/TestGena
   ```

2. **Navigate to the Project Directory**: Change directory to enter the project folder.

   ```bash
   cd TestGena
   ```

3. **Install the Library**: Execute the setup.py script to install the `code_dependency_grapher` library.

   ```bash
   python3 -m pip install -e .
   ```

These steps will set up the necessary environment for using the library in your local development environment.

## Usage

### Running the Code Dependency Grapher Example Script
To execute the usage example script of our library, use the following command:

```bash
python -m code_dependency_grapher.usage_examples.building_dependency_graph
```

This script demonstrates how to utilize the Code Dependency Grapher library.

### Example Usage Script
```python
from code_dependency_grapher.cdg.repository_processors import GraphBuilder, JsonConverter, RepositoryContainer, Compose, CloneRepository

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed", "/home/db")
Compose(repo_container, [CloneRepository("https://github.com/arXiv/arxiv-feed"), GraphBuilder(), JsonConverter()])
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

- **RegExpFinder**: Searches components by name in the repository container and returns the `CodeComponent` class.
  **Example**: 
  ```python
  Compose(repo_container, [RegExpFinder(r'\bfeed\.routes\.status\b')])
  ```

- **Compose**: Executes a sequence of other processors on the repository container.
  - **Input**: `in_place: bool = True`.
  **Example**: 
  ```python
  Compose(repo_container, [Processors_list])
  ```

  If using `in_place = False`, call the `get_processed_container` function.
  **Example**: 
  ```python
  processed_container = Compose(repo_container, [Processors_list], in_place=False).get_processed_container()
  ```
  
This set of processors allows flexible management and analysis of code dependencies within repositories.

### List of repository processors:
- **CloneRepository**: This processor clones repository from given git url.
**Example**: 
```python 
Compose(repository_container, [CloneRepository("https://github.com/arXiv/arxiv-feed")])
```

- **GraphBuilder**: This processor builds graph of the given repository and saves it into the defined ``db_path``, also GraphBuilder fills given repository container.
**Example**: 
```python 
Compose(repository_container, [GraphBuilder()])
```
- **GraphUpdater**: This processor updates graph of the given repository and changes the ``json`` file according to updates, also refine given repository container.
**Example**: 
```python 
Compose(repository_container, [GraphUpdater()])
```
- **JsonConverter**: This processor convertes fields of the given ``repository container`` into the ``json`` file, placed according to given ``db_path``.
**Example**: 
```python 
Compose(repository_container, [JsonConverter()])
```
- **JsonDeconverter**: This processor deconvertes ``json`` from ``repository_container.db_path`` field and fills in all attributes of ``repository_container``.
**Example**: 
```python 
Compose(repository_container, [JsonDeconverter()])
```
- **RegExpFinder**: This processor searches components by name in given ``repository container``, returns ``CodeComponent`` class.
**Example**: 
```python 
Compose(repository_container, [RegExpFinder(r'\bfeed\.routes\.status\b')])
```
- **Compose**: This is processor to execute sequence of the other processors on the given ``repository_container``, has input value: ``in_place: bool = True``.
**Example**: 
```python 
Compose(repository_container, [Processors_list])
```
If you're using ``in_place = False``, you need to call function ``get_processed_container``
**Example**: 
```python 
processed_container = Compose(repository_container, [Processors_list], in_place=False).get_processed_container()
```
### JSON Tree Structure Description

After running the analysis, the JSON structure stored at `db_url` will have the following format:

#### Top-Level Structure:
- `files`: A list of dictionaries, each representing a file analyzed.
- `components`: A list of dictionaries, each representing a component (function or class) identified within the files.
- `external_components`: A list of ids of external import statements (components outside the parsed repo)

#### `files` List:
Each dictionary in the `files` list contains:
- `file_id`: A unique identifier for the file.
- `file_path`: The relative path to the file.
- `imports`: A list of strings representing all imported modules and components in the file.
- `called_components`: A list of strings representing all components or functions called within the file.
- `callable_components`: A list of strings representing all functions or classes defined in the file that can be called.

#### `components` List:
Each dictionary in the `components` list contains:
- `component_id`: A unique identifier for the component.
- `component_name`: The full name of the component, including its module or file context.
- `component_code`: The actual code of the component.
- `linked_component_ids`: A list of component IDs representing other components that are linked or associated with this component.
- `file_id`: The ID of the file  that processed this component.
- `external_component_ids`: A list of IDs representing external components that this component interacts with.

This structure helps in understanding the relationships and dependencies among various files and components in the project.

### Real Example of the json:
```json
{
    "external_components": {
        "71507f0f-0ead-4018-a8cb-d3b864ea4d8d": "flask.make_response",
        "c1327f0a-b679-4c91-aa98-e4ccd2ed4b73": "flask.current_app",
        "782625df-3b8b-4cee-b489-ac154218837d": "werkzeug.Response",
        "a86d2d45-583e-4bf1-8288-2d4131cdef9a": "datetime.timedelta",
        "f0b71cae-cd18-4553-acdb-995e084d5d63": "feed.controller",
        "ba9aa62c-98a5-4fa8-a304-7feca050602e": "typing.Union",
        "8f02e12b-1bcc-4df2-98f9-6f74f425f8e3": "flask.url_for",
        "7e681eb7-b586-4714-8d6b-141fc1867068": "flask.request",
        "39ee80b7-694e-4c95-bf95-985954706490": "flask.redirect",
        "4c1fcfc4-5814-49f6-b247-e9e7d0e91338": "feed.fetch_data",
        "fa0a477f-522c-4500-8c92-787c0add84db": "typing.List",
        "dd1387f3-f925-4538-b060-7317fb24a8f5": "enum.Enum",
        "602cd41f-9e43-4aca-83ee-a661625272c0": "typing.Set",
        "acd4fafd-ecf7-49a0-ab0a-9485c1a7b555": "datetime.datetime",
        "3700e526-dc75-4106-81f8-f6a289b1a982": "datetime.timezone",
        "52d99806-5357-4b7f-86aa-ce821f3b7287": "zoneinfo.ZoneInfo",
        "5067c463-9782-4a90-b29c-d7deae28cc26": "random",
        "f6a3f2b5-6502-4e6e-988f-188488a3524f": "feed.consts.DELIMITER",
        "b7f35d4e-c23c-4bbc-848c-9c694bcff72e": "hashlib",
        "091e0e65-1d7a-4bee-8a9c-8b2e5a7855a0": "feed.consts",
        "50f4c340-97bf-48c6-91fd-fef2a635ddbf": "typing.Tuple",
        "d77f1e98-07ff-47c5-96ad-c6fcf177a12d": "os",
        "908cf5ae-16bd-49ba-b2d7-7dc87b548033": "arxiv.config",
        "250cdcfb-3d31-4e38-a73f-367cf1487027": "flask.Flask",
        "76d4e277-9296-4c12-a8d3-a1da40532789": "feed.routes",
        "b14d5824-9035-43e8-97ae-318ffcb47e9e": "arxiv.base.Base"
    
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
