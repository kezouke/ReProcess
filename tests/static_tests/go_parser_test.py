import pytest
import tempfile
import os
from reprocess.parsers import GoFileParser, GoComponentFillerHelper


@pytest.fixture(scope='session')
def go_code_file():
    """
    Fixture to generate a Go code file with functions,
    write it to a temporary file, and return the path to the file and the temporary folder name.
    """
    # Sample C code to be written to the file
    go_code = r"""package main

import (
	"fmt"
	"example/mathutils"
)

// Global variables
var (
    globalCounter int    = 0
    globalMessage string = "Hello, Global Variables!"
)

var count int
count = 5

test := 0

var x, y, z int = 1, 2, 3


func incrementCounter() {
    globalMessage = "Global Variables are updated!"
}
"""

    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'GeneratedCode.go')

        # Write the C code to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(go_code)

        # Return the path and directory name
        yield temp_file_path, os.path.basename(temp_dir)


def test_go_file_parser(go_code_file):
    file_path, temp_dir_name = go_code_file
    parser = GoFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['GeneratedCode.incrementCounter',
                                  'GeneratedCode.count',
                                  'GeneratedCode.x',
                                  'GeneratedCode.test',
                                  'GeneratedCode.globalMessage',
                                  'GeneratedCode.y',
                                  'GeneratedCode.z',
                                  'GeneratedCode.globalCounter']), \
            "Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(), \
            "Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['incrementCounter']), \
            "Wrong callable components extraction!"


def test_go_component_filler_helper(go_code_file):
    file_path, temp_dir_name = go_code_file
    parser = GoFileParser(file_path, temp_dir_name)

    helper = GoComponentFillerHelper("GeneratedCode.incrementCounter",
                                     file_path, parser)

    code = helper.extract_component_code()
    assert "func incrementCounter() {" in code
    assert helper.component_type == "function"
    assert 'globalMessage = "Global Variables are updated!"' in code

    to_link = helper.extract_callable_objects()
    assert set(to_link) == set(['GeneratedCode.globalMessage'])
