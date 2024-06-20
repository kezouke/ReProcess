# Code Dependency Grapher README

## Introduction
The Code Dependency Grapher is a tool designed to manage dependencies within code repositories. This document provides instructions on how to set up and use the current version of the Code Dependency Grapher.

## Installation
1. **Clone the Repository**: First, clone the Code Dependency Grapher repository to your local machine.

   ```bash
   git clone https://github.com/kezouke/TestGena
   ```

2. **Navigate to the Project Directory**: Change your working directory to the project directory.

   ```bash
   cd code_dependency_grapher
   ```

## Usage

### Running the Code Dependency Grapher
To run the Code Dependency Grapher, you need to execute the `build_dependency_graph.py` script by using command: ``python -m code_dependency_grapher.usage_examples.building_dependency_graph``.

Below is an example script illustrating how to use the script.

### Example Usage
```python
from code_dependency_grapher.cdg.repository_processors import GraphBuilder, JsonConverter, RepositoryContainer, Compose, CloneRepository

repo_container = RepositoryContainer("arxiv-feed", "/home/arxiv-feed",
                                     "/home/db")
Compose(repo_container, [CloneRepository("https://github.com/arXiv/arxiv-feed"), GraphBuilder(), JsonConverter()])
```

### Parameters of the repository container
- **repo_name**: This is the name of repository
- **repo_path**: This is the directory where the repository will be cloned.
- **db_path**: This is the directory where the JSON graphs will be saved.

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
    "author": "78058179+kyokukou@users.noreply.github.com",
    "commit hash": "3720f2018d8e59b6c760de53f515e7eda0ed16c7",
    "files": [
        {
            "file_id": "741f8448-61ac-4e51-91ee-ec269aa7790d",
            "file_path": "main.py",
            "imports": [
                "sys",
                "QApplication",
                "QStackedWidget",
                "MainWindow",
                "Get_info_byID",
                "Set_total_forCheck",
                "CreateCheck",
                "GetLastIdCheck",
                "UpdateIdCheck",
                "UpdateIdCheckInRelation",
                "DelCheck",
                "CreateFile"
            ],
            "called_components": [
                "QApplication",
                "show",
                "exec_",
                "MainWindow",
                "addWidget",
                "QStackedWidget",
                "Get_info_byID"
            ],
            "callable_components": [
                "application"
            ]
        }
    ],
    "components": [
        {
            "component_id": "9a24def5-ed4b-4042-90f2-1e7f3118d514",
            "component_name": "modules.help.CreateCheck",
            "component_code": "from sqLite import models\nimport datetime\n\ndef CreateCheck(seller_name: str, shop_name: str, id_amount: dict):\n    with models.db:\n        tmp = models.Check(date=datetime.date.today(), total=0, shop_name=shop_name, seller_name=seller_name)\n        tmp.save()\n        idx = tmp.id\n        for i in id_amount:\n            models.PurchasesCheck.create(id_purchases=models.Purchases[i], id_check=models.Check[idx], amount=id_amount[i])\n        Set_total_forCheck(idx)",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f",
                "a77f26ab-f03a-4325-9b64-96e640594a13"
            ]
        }
    ],
    "external_components": [
        {
            "de5df083-3308-41d9-87f4-6ffcfe745d8e": "sys",
            "a615fc16-f499-4170-8779-2a0cd35f5d79": "modules.interface.MainWindow",
            "b0bf9462-ec33-41f3-b640-d936f0f9b43b": "PyQt5.QtWidgets.QStackedWidget",
            "20d430d9-239d-4de4-96b0-257db1623d58": "PyQt5.QtWidgets.QApplication",
            "abfecef1-40af-4a92-a162-27e3d02addf8": "PyQt5.QtWidgets.QDesktopWidget",
            "62ad851c-e96a-46d8-a2c1-8f5768db724f": "sqLite.models",
            "1b180018-2544-485e-a6eb-8c7497db4497": "PyQt5.uic.loadUi",
            "8847f430-ee64-44e9-80ab-2153047712f7": "numpy",
            "6206341c-a81d-4940-b92a-f279f349a0a9": "PyQt5.QtWidgets.QMessageBox",
            "22326557-c07b-4fff-9a9f-8f6f7961e966": "PyQt5.QtCore",
            "2b226fc1-148c-4d39-9fbc-5243d47ed35e": "PyQt5.QtWidgets.QTableWidgetItem",
            "4f8f22a9-437f-4d8d-9bd4-31c71c1238b8": "PyQt5.QtWidgets.QWidget",
            "9eeca0d3-a1ca-4391-befc-180d54b7ff07": "modules.pows.tryParseInt",
            "a77f26ab-f03a-4325-9b64-96e640594a13": "datetime"
        }
    ]
}
```
