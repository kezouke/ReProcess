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

### Running the Engine
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
        },
        {
            "file_id": "78989791-10b5-440b-97af-fbbaa2449065",
            "file_path": "modules/add_From.py",
            "imports": [
                "sys",
                "QtCore",
                "Get_info_byID",
                "Set_total_forCheck",
                "CreateCheck",
                "GetLastIdCheck",
                "UpdateIdCheck",
                "UpdateIdCheckInRelation",
                "DelCheck",
                "CreateFile",
                "QMainWindow",
                "QWidget",
                "QDesktopWidget",
                "QTableWidgetItem",
                "loadUi",
                "QMessageBox",
                "m",
                "foo",
                "np"
            ],
            "called_components": [
                "CreateCheck",
                "foo",
                "__init__",
                "super",
                "keys",
                "freezCol",
                "print",
                "frameGeometry",
                "currentText",
                "abs",
                "show",
                "addItem",
                "topLeft",
                "move",
                "loadUi",
                "setFlags",
                "item",
                "connect",
                "setFixedSize",
                "setWindowTitle",
                "setupNames",
                "add_functions_for_buttons",
                "range",
                "setCurrentText",
                "ShowError",
                "append",
                "insert",
                "setIcon",
                "moveCenter",
                "QMessageBox",
                "exec_",
                "QDesktopWidget",
                "setItem",
                "setText",
                "availableGeometry",
                "clear",
                "insertRow",
                "center",
                "rowCount",
                "QTableWidgetItem",
                "str",
                "text",
                "select",
                "close",
                "len"
            ],
            "callable_components": [
                "FormAdd"
            ]
        },
        {
            "file_id": "29396126-729e-44f8-9265-090ea7fded8e",
            "file_path": "modules/del_Form.py",
            "imports": [
                "sys",
                "QMainWindow",
                "QWidget",
                "QDesktopWidget",
                "QTableWidgetItem",
                "loadUi",
                "QMessageBox",
                "Get_info_byID",
                "DelCheck",
                "tryParseInt"
            ],
            "called_components": [
                "toPlainText",
                "__init__",
                "super",
                "frameGeometry",
                "show",
                "topLeft",
                "move",
                "loadUi",
                "tryParseInt",
                "connect",
                "setFixedSize",
                "setWindowTitle",
                "add_functions_for_buttons",
                "join",
                "ShowError",
                "insert",
                "setIcon",
                "moveCenter",
                "QMessageBox",
                "exec_",
                "QDesktopWidget",
                "setItem",
                "setText",
                "availableGeometry",
                "insertRow",
                "center",
                "rowCount",
                "QTableWidgetItem",
                "str",
                "DelCheck",
                "close",
                "Get_info_byID"
            ],
            "callable_components": [
                "DelForm"
            ]
        },
        {
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "file_path": "modules/help.py",
            "imports": [
                "datetime",
                "sys",
                "models"
            ],
            "called_components": [
                "update",
                "Set_total_forCheck",
                "len",
                "create",
                "print",
                "delete",
                "Check",
                "sum",
                "range",
                "enumerate",
                "save",
                "GetLastIdCheck",
                "append",
                "insert",
                "UpdateIdCheckInRelation",
                "write",
                "today",
                "UpdateIdCheck",
                "str",
                "open",
                "select",
                "close",
                "where",
                "execute",
                "join"
            ],
            "callable_components": [
                "CreateCheck",
                "GetLastIdCheck",
                "UpdateIdCheckInRelation",
                "Set_total_forCheck",
                "DelCheck",
                "UpdateIdCheck",
                "CreateFile",
                "Get_info_byID"
            ]
        },
        {
            "file_id": "664ea422-c875-4d60-a6b2-168b17fe99cd",
            "file_path": "modules/tests/tests_add_from.py",
            "imports": [],
            "called_components": [
                "print"
            ],
            "callable_components": [
                "foo"
            ]
        }
    ],
    "components": [
        {
            "component_id": "e614d8b7-1871-48f2-916a-f510c664a17c",
            "component_name": "main.application",
            "component_code": "from modules.help import Get_info_byID\nfrom modules.interface import MainWindow\nfrom PyQt5.QtWidgets import QApplication, QStackedWidget\nimport sys\n\ndef application():\n    app = QApplication(sys.argv)\n    main_window = MainWindow()\n    widget = QStackedWidget()\n    widget.addWidget(main_window)\n    widget.show()\n    app.exec_()\n    Get_info_byID(3)",
            "linked_component_ids": [
                "8564c378-b9d7-422c-b982-267a68d3db8d"
            ],
            "file_id": "741f8448-61ac-4e51-91ee-ec269aa7790d",
            "external_component_ids": [
                "de5df083-3308-41d9-87f4-6ffcfe745d8e",
                "a615fc16-f499-4170-8779-2a0cd35f5d79",
                "b0bf9462-ec33-41f3-b640-d936f0f9b43b",
                "20d430d9-239d-4de4-96b0-257db1623d58"
            ]
        },
        {
            "component_id": "3f2582dd-95b9-43b1-b578-41751600424d",
            "component_name": "modules.add_From.FormAdd",
            "component_code": "import numpy as np\nfrom modules.tests.tests_add_from import foo\nfrom sqLite import models as m\nfrom PyQt5.QtWidgets import QMessageBox\nfrom PyQt5.uic import loadUi\nfrom PyQt5.QtWidgets import QWidget, QDesktopWidget, QTableWidgetItem\nfrom modules.help import CreateCheck\nfrom PyQt5 import QtCore\n\nclass FormAdd(QWidget):\n    \"\"\" \u041a\u043b\u0430\u0441\u0441 \u0433\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0430 \u0434\u043b\u044f \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0444\u043e\u0440\u043c\u044b \"\"\"\n\n    def __init__(self, parent) -> None:\n        \"\"\" \u0418\u043d\u0438\u0446\u0430\u0438\u043b\u0438\u0437\u0430\u0446\u0438\u044f \"\"\"\n        super(FormAdd, self).__init__()\n        self.parent = parent\n        loadUi('ui_files/addForm.ui', self)\n        self.add_functions_for_buttons()\n        self.setFixedSize(1000, 710)\n        self.setWindowTitle('Add')\n        self.center()\n        self.shops_sallers_name = {}\n        self.setupNames()\n\n    def freezCol(self, txt):\n        tmp = QTableWidgetItem()\n        tmp.setText(str(txt))\n        tmp.setFlags(QtCore.Qt.ItemIsEnabled)\n        np.abs(-10)\n        return tmp\n\n    def setupNames(self):\n        names = []\n        cost = []\n        foo()\n        with m.db:\n            query = m.Purchases.select()\n            for res in query:\n                names.append(res.purchases_name)\n                cost.append(res.cost)\n        for i in range(len(names)):\n            rowPosition = self.tableWidget.rowCount()\n            self.tableWidget.insertRow(rowPosition)\n            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(self.freezCol(names[i])))\n            self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(self.freezCol(cost[i])))\n            self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(str(0)))\n        self.shops_sallers_name = {'\u041f\u044f\u0442\u0435\u0440\u043e\u0447\u043a\u0430': ['\u0411\u043b\u043e\u0445\u0438\u043d\u0430 \u0415\u043a\u0430\u0442\u0435\u0440\u0438\u043d\u0430 \u042e\u0440\u044c\u0435\u0432\u043d\u0430', '\u041f\u0430\u0432\u043b\u043e\u0432 \u0424\u0451\u0434\u043e\u0440 \u0414\u0435\u043c\u044c\u044f\u043d\u043e\u0432\u0438\u0447', '\u0424\u0438\u043b\u0438\u043f\u043f\u043e\u0432\u0430 \u0410\u0434\u0435\u043b\u0438\u043d\u0430 \u041c\u0430\u0442\u0432\u0435\u0435\u0432\u043d\u0430'], '\u041c\u0430\u0433\u043d\u0438\u0442': ['\u041b\u044b\u043a\u043e\u0432\u0430 \u0410\u043b\u0435\u043a\u0441\u0430\u043d\u0434\u0440\u0430 \u0410\u0440\u0441\u0435\u043d\u0442\u044c\u0435\u0432\u043d\u0430', '\u0424\u0438\u043b\u0438\u043f\u043f\u043e\u0432\u0430 \u0421\u043e\u0444\u0438\u044f \u0412\u043b\u0430\u0434\u0438\u043c\u0438\u0440\u043e\u0432\u043d\u0430', '\u0416\u0443\u043a\u043e\u0432 \u0421\u0435\u0440\u0430\u0444\u0438\u043c \u0414\u0435\u043d\u0438\u0441\u043e\u0432\u0438\u0447'], '\u042d\u0434\u0435\u043b\u044c\u0432\u0435\u0439\u0441': ['\u0422\u0438\u0445\u043e\u043d\u043e\u0432 \u0418\u043b\u044c\u044f \u0414\u0430\u043d\u0438\u0438\u043b\u043e\u0432\u0438\u0447', '\u041f\u0430\u0432\u043b\u043e\u0432 \u0410\u043b\u0435\u043a\u0441\u0430\u043d\u0434\u0440 \u0414\u043c\u0438\u0442\u0440\u0438\u0435\u0432\u0438\u0447', '\u0412\u0430\u0441\u0438\u043b\u044c\u0435\u0432 \u041c\u0438\u0445\u0430\u0438\u043b \u041b\u044c\u0432\u043e\u0432\u0438\u0447']}\n        for i in self.shops_sallers_name:\n            self.ShopName.addItem(i)\n        self.ShopName.setCurrentText('')\n\n    def Creation(self):\n        changes = {}\n        for i in range(self.tableWidget.rowCount()):\n            text = self.tableWidget.item(i, 2).text()\n            if text != '0':\n                changes[i + 1] = text\n        if len(changes.keys()) != 0:\n            CreateCheck(seller_name=self.SellerName.currentText(), shop_name=self.ShopName.currentText(), id_amount=changes)\n            self.ShowError('\u0427\u0435\u043a \u0441\u043e\u0437\u0434\u0430\u043d')\n        else:\n            self.ShowError('\u041d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e \u0441\u043e\u0437\u0434\u0430\u0442\u044c \u0447\u0435\u043a, \u0442\u0430\u043a \u043a\u0430\u043a \u0432\u044b \u043d\u0435 \u0434\u043e\u0431\u0430\u0432\u0438\u043b\u0438 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u044b')\n        print(changes)\n\n    def add_functions_for_buttons(self) -> None:\n        \"\"\" \u041c\u0435\u0442\u043e\u0434 \u0434\u043b\u044f \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u0444\u0443\u043d\u043a\u0446\u0438\u0439 \u0434\u043b\u044f \u043a\u043d\u043e\u043f\u043e\u043a \"\"\"\n        self.backtoprev.clicked.connect(self.backtomenu)\n        self.CreateButton.clicked.connect(self.Creation)\n        self.ShopName.currentIndexChanged.connect(self.test1)\n\n    def test1(self):\n        self.SellerName.clear()\n        for i in self.shops_sallers_name:\n            if self.ShopName.currentText() == i:\n                for j in self.shops_sallers_name[i]:\n                    self.SellerName.addItem(j)\n\n    def backtomenu(self):\n        self.close()\n        self.parent.show()\n\n    def center(self):\n        qr = self.frameGeometry()\n        cp = QDesktopWidget().availableGeometry().center()\n        qr.moveCenter(cp)\n        self.move(qr.topLeft())\n\n    def ShowError(self, errorText: str) -> None:\n        \"\"\"\u041c\u0435\u0442\u043e\u0434 \u0434\u043b\u044f \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u043e\u0448\u0438\u0431\u043a\u0438\"\"\"\n        msg = QMessageBox()\n        msg.setIcon(QMessageBox.Information)\n        msg.setText(errorText)\n        msg.setWindowTitle('Attantion')\n        msg.exec_()",
            "linked_component_ids": [
                "9a24def5-ed4b-4042-90f2-1e7f3118d514",
                "bb090e76-980d-45de-bc4e-d9526015f867"
            ],
            "file_id": "78989791-10b5-440b-97af-fbbaa2449065",
            "external_component_ids": [
                "abfecef1-40af-4a92-a162-27e3d02addf8",
                "62ad851c-e96a-46d8-a2c1-8f5768db724f",
                "1b180018-2544-485e-a6eb-8c7497db4497",
                "8847f430-ee64-44e9-80ab-2153047712f7",
                "6206341c-a81d-4940-b92a-f279f349a0a9",
                "22326557-c07b-4fff-9a9f-8f6f7961e966",
                "2b226fc1-148c-4d39-9fbc-5243d47ed35e",
                "4f8f22a9-437f-4d8d-9bd4-31c71c1238b8"
            ]
        },
        {
            "component_id": "155b586c-f63a-4b43-ad1a-b8f42492747f",
            "component_name": "modules.del_Form.DelForm",
            "component_code": "from modules.pows import tryParseInt\nfrom modules.help import Get_info_byID, DelCheck\nfrom PyQt5.QtWidgets import QMessageBox\nfrom PyQt5.uic import loadUi\nfrom PyQt5.QtWidgets import QWidget, QDesktopWidget, QTableWidgetItem\n\nclass DelForm(QWidget):\n    \"\"\" \u041a\u043b\u0430\u0441\u0441 \u0433\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0430 \u0434\u043b\u044f \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0444\u043e\u0440\u043c\u044b \"\"\"\n\n    def __init__(self, parent) -> None:\n        \"\"\" \u0418\u043d\u0438\u0446\u0430\u0438\u043b\u0438\u0437\u0430\u0446\u0438\u044f \"\"\"\n        super(DelForm, self).__init__()\n        self.parent = parent\n        loadUi('ui_files\\\\delForm.ui', self)\n        self.add_functions_for_buttons()\n        self.setFixedSize(1000, 710)\n        self.setWindowTitle('Remove')\n        self.center()\n\n    def add_functions_for_buttons(self) -> None:\n        \"\"\" \u041c\u0435\u0442\u043e\u0434 \u0434\u043b\u044f \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u0444\u0443\u043d\u043a\u0446\u0438\u0439 \u0434\u043b\u044f \u043a\u043d\u043e\u043f\u043e\u043a \"\"\"\n        self.backtoprev.clicked.connect(self.backtomenu)\n        self.checkButt.clicked.connect(self.preview)\n        self.remButt.clicked.connect(self.DelByID)\n\n    def DelByID(self):\n        (id, f) = tryParseInt(self.idxInput.toPlainText())\n        if f:\n            DelCheck(id)\n        else:\n            self.ShowError('\u0427\u0442\u043e-\u0442\u043e \u043d\u0435 \u0442\u0430\u043a \u0441 \u0438\u043d\u0434\u0435\u043a\u0441\u043e\u043c')\n\n    def preview(self):\n        (id, f) = tryParseInt(self.idxInput.toPlainText())\n        if f:\n            (req, cost, amount, name_prod) = Get_info_byID(id)\n            rowPosition = self.tableWidget.rowCount()\n            self.tableWidget.insertRow(rowPosition)\n            str1 = ', '.join(name_prod)\n            try:\n                tmp = req[0]\n                self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(req[0]))\n                self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(req[2]))\n                self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(req[3]))\n                self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(str1))\n                self.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(str(req[1])))\n            except Exception:\n                self.ShowError('\u0414\u0430\u043d\u043d\u043e\u0433\u043e \u0438\u043d\u0434\u0435\u043a\u0441\u0430 \u043d\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442!')\n        else:\n            self.ShowError('\u0412\u044b \u043d\u0435 \u0432\u0432\u0435\u043b\u0438 \u0438\u043d\u0434\u0435\u043a\u0441')\n\n    def backtomenu(self):\n        self.close()\n        self.parent.show()\n\n    def center(self):\n        qr = self.frameGeometry()\n        cp = QDesktopWidget().availableGeometry().center()\n        qr.moveCenter(cp)\n        self.move(qr.topLeft())\n\n    def ShowError(self, errorText: str) -> None:\n        \"\"\"\u041c\u0435\u0442\u043e\u0434 \u0434\u043b\u044f \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u043e\u0448\u0438\u0431\u043a\u0438\"\"\"\n        msg = QMessageBox()\n        msg.setIcon(QMessageBox.Critical)\n        msg.setText(errorText)\n        msg.setWindowTitle('Attantion')\n        msg.exec_()",
            "linked_component_ids": [
                "c57b9bc1-7419-48e8-98ac-a1fe44d8957a",
                "8564c378-b9d7-422c-b982-267a68d3db8d"
            ],
            "file_id": "29396126-729e-44f8-9265-090ea7fded8e",
            "external_component_ids": [
                "abfecef1-40af-4a92-a162-27e3d02addf8",
                "1b180018-2544-485e-a6eb-8c7497db4497",
                "9eeca0d3-a1ca-4391-befc-180d54b7ff07",
                "6206341c-a81d-4940-b92a-f279f349a0a9",
                "2b226fc1-148c-4d39-9fbc-5243d47ed35e",
                "4f8f22a9-437f-4d8d-9bd4-31c71c1238b8"
            ]
        },
        {
            "component_id": "8564c378-b9d7-422c-b982-267a68d3db8d",
            "component_name": "modules.help.Get_info_byID",
            "component_code": "from sqLite import models\n\ndef Get_info_byID(idx: int):\n    req = []\n    with models.db:\n        (cost, amount, name_prod) = Set_total_forCheck(idx)\n        quary = models.Check.select().where(models.Check.id == idx)\n        for res in quary:\n            req.append(str(res.date))\n            req.append(res.total)\n            req.append(res.shop_name)\n            req.append(res.seller_name)\n        return (req, cost, amount, name_prod)",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
        {
            "component_id": "d77e9610-37f8-4132-a061-ec9d93e76223",
            "component_name": "modules.help.Set_total_forCheck",
            "component_code": "from sqLite import models\n\ndef Set_total_forCheck(idx: int):\n    cost = []\n    amount = []\n    name_prod = []\n    with models.db:\n        quary = models.Purchases.select().join(models.PurchasesCheck).where(models.PurchasesCheck.id_check == idx)\n        for res in quary:\n            cost.append(res.cost)\n            name_prod.append(res.purchases_name)\n        quary = models.PurchasesCheck.select().where(models.PurchasesCheck.id_check == idx)\n        for res in quary:\n            amount.append(res.amount)\n        res = sum([cost[i] * amount[i] for i in range(len(cost))])\n        update = models.Check.update(total=res).where(models.Check.id == idx)\n        update.execute()\n        return (cost, amount, name_prod)",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
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
        },
        {
            "component_id": "aa8a5358-c525-4132-be54-9556fd7e7ae6",
            "component_name": "modules.help.GetLastIdCheck",
            "component_code": "from sqLite import models\n\ndef GetLastIdCheck():\n    last = -1\n    with models.db:\n        queru = models.Check.select()\n        for res in queru:\n            last = res.id\n    return last",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
        {
            "component_id": "6ea6d987-5dbb-4d23-8782-89543384bb81",
            "component_name": "modules.help.UpdateIdCheck",
            "component_code": "from sqLite import models\n\ndef UpdateIdCheck(old: int, new: int):\n    with models.db:\n        query = models.Check.update(id=new).where(models.Check.id == old)\n        query.execute()",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
        {
            "component_id": "19d38d1b-92f6-474c-9304-5bb914f1a2e1",
            "component_name": "modules.help.UpdateIdCheckInRelation",
            "component_code": "from sqLite import models\n\ndef UpdateIdCheckInRelation(old: int, new: int):\n    with models.db:\n        query = models.PurchasesCheck.update(id_check=new).where(models.PurchasesCheck.id_check == old)\n        query.execute()",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
        {
            "component_id": "c57b9bc1-7419-48e8-98ac-a1fe44d8957a",
            "component_name": "modules.help.DelCheck",
            "component_code": "from sqLite import models\n\ndef DelCheck(idx: int):\n    last = GetLastIdCheck()\n    with models.db:\n        q1 = models.PurchasesCheck.delete().where(models.PurchasesCheck.id_check == idx)\n        q2 = models.Check.delete().where(models.Check.id == idx)\n        q1.execute()\n        q2.execute()\n        UpdateIdCheck(last, idx)\n        UpdateIdCheckInRelation(last, idx)",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
        {
            "component_id": "977f9f14-4d9f-40a1-97f8-05b118f450cf",
            "component_name": "modules.help.CreateFile",
            "component_code": "from sqLite import models\n\ndef CreateFile():\n    with models.db:\n        query = models.Check.select()\n        q1 = models.Purchases.select()\n        q2 = models.PurchasesCheck.select()\n        s1 = {}\n        s2 = {}\n        s3 = {}\n        for (idx, res) in enumerate(query):\n            s1[idx] = [res.id, str(res.date), res.total]\n        for (idx, res) in enumerate(q1):\n            s2[idx] = [res.id, res.purchases_name, res.cost]\n        for (idx, res) in enumerate(q2):\n            s3[idx] = [str(res.id_check), str(res.id_purchases)]\n        print(s1, s2, s3, sep='\\n')\n        open('sqLite/foo.txt', 'w').close()\n        with open('sqLite/foo.txt', 'a') as fp:\n            for i in s1:\n                fp.write(str(i) + ' ' + str(s1[i]) + '\\n')\n            for i in s2:\n                fp.write('\\n')\n                fp.write(str(i) + ' ' + str(s2[i]) + '\\n')\n            for i in s3:\n                fp.write('\\n')\n                fp.write(str(i) + ' ' + str(s3[i]) + '\\n')",
            "linked_component_ids": [],
            "file_id": "de787a2d-e36c-4c19-8000-9b0a3bb3dd76",
            "external_component_ids": [
                "62ad851c-e96a-46d8-a2c1-8f5768db724f"
            ]
        },
        {
            "component_id": "bb090e76-980d-45de-bc4e-d9526015f867",
            "component_name": "modules.tests.tests_add_from.foo",
            "component_code": "\ndef foo():\n    print('foooo')",
            "linked_component_ids": [],
            "file_id": "664ea422-c875-4d60-a6b2-168b17fe99cd",
            "external_component_ids": []
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
