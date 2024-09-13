import pytest
import tempfile
import os
from reprocess.parsers.c_parsers import CFileParser, CComponentFillerHelper


@pytest.fixture(scope='session')
def c_code_file():
    """
    Fixture to generate a C code file with functions,
    write it to a temporary file, and return the path to the file and the temporary folder name.
    """
    # Sample C code to be written to the file
    c_code = r"""
#include <stdio.h>

void sampleFunction(int x, int y) {
    printf("Sample function called with x=%d and y=%d\n", x, y);
}

int anotherFunction(int a) {
    if (a > 10) {
        return a * 2;
    } else {
        return a - 2;
    }
}

int main() {
    sampleFunction(5, 7);
    printf("%d\n", anotherFunction(15));
    return 0;
}
"""

    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'GeneratedCode.c')

        # Write the C code to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(c_code)

        # Return the path and directory name
        yield temp_file_path, os.path.basename(temp_dir)


def test_c_file_parser(c_code_file):
    file_path, temp_dir_name = c_code_file
    parser = CFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['sampleFunction',
                                  'anotherFunction',
                                  'main']), \
            "Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(['printf',
                                          'sampleFunction',
                                          'anotherFunction']), \
            "Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['sampleFunction',
                                            'anotherFunction',
                                            'main']), \
            "Wrong callable components extraction!"


def test_c_component_filler_helper(c_code_file):
    file_path, temp_dir_name = c_code_file
    parser = CFileParser(file_path, temp_dir_name)

    helper = CComponentFillerHelper("sampleFunction", file_path, parser)

    code = helper.extract_component_code()
    assert "void sampleFunction(int x, int y)" in code
    assert helper.component_type == "function"
    assert "printf(\"Sample function called with x=%d and y=%d\\n\", x, y);" in code

    to_link = helper.extract_callable_objects()
    assert set(to_link) == set(['printf'])
