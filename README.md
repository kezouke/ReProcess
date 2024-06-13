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
To run the Code Dependency Grapher, you will need to execute the `Engine.py` script. Below is an example script illustrating how to use the Engine.

### Example Usage
```python
import os
from code_dependency_grapher.Engine import Engine

# Define the paths
db_url = "/home/db"  # Directory where JSON graphs will be saved
repos_dir = "/home/repos/"  # Directory where repositories will be cloned/stored

# Initialize the Engine
engine = Engine(db_url, repos_dir)

# Make a request to fetch data from a repository
repo_url = "https://github.com/showpiecep/SQLite_PyQt"
engine.request(repo_url)

# Additional requests can be made as needed
# engine.request("https://github.com/vllm-project/vllm")
# engine.request("https://github.com/IU-Capstone-Project-2024/SayNoMore")
```

### Parameters
- **db_url**: This is the directory where the JSON graphs will be saved.
- **repos_dir**: This is the directory where the repositories will be cloned and stored.
- **repo_url**: The URL of the repository from which you want to fetch data.
