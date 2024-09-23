import pytest
import tempfile
import os
from reprocess.parsers.cpp_parsers import CppFileParser, CppComponentFillerHelper


@pytest.fixture(scope='session')
def cpp_code_file():
    """
    Fixture to generate a C++ code file with classes, methods, and functions,
    write it to a temporary file, and return the path to the file and the temporary folder name.
    """
    # Sample C++ code to be written to the file
    cpp_code = r"""
#include <iostream>

class SampleClass {
public:
    SampleClass(const std::string& name) : name(name) {}

    std::string greet() {
        return "Hello, " + name + "!";
    }

    static void sampleMethod(int x, int y) {
        std::cout << "Sample method called with x=" << x << " and y=" << y << std::endl;
    }

    int anotherMethod(int a) {
        if (a > 10) {
            return a * 2;
        } else {
            return a - 2;
        }
    }

private:
    std::string name;
};

int main() {
    SampleClass sc("World");
    std::cout << sc.greet() << std::endl;
    SampleClass::sampleMethod(5, 7);
    std::cout << sc.anotherMethod(15) << std::endl;
    return 0;
}
"""

    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'GeneratedCode.cpp')

        # Write the C++ code to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(cpp_code)

        # Return the path and directory name
        yield temp_file_path, os.path.basename(temp_dir)


def test_cpp_file_parser(cpp_code_file):
    file_path, temp_dir_name = cpp_code_file
    parser = CppFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['SampleClass',
                                  'SampleClass.SampleClass',
                                  'SampleClass.greet',
                                  'SampleClass.sampleMethod',
                                  'SampleClass.anotherMethod',
                                  'main']), \
            "Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(['SampleClass.greet',
                                          'SampleClass.sampleMethod',
                                          'SampleClass.anotherMethod',
                                          'std::cout']), \
            "Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['SampleClass',
                                            'SampleClass.SampleClass'
                                            'SampleClass.sampleMethod',
                                            'SampleClass.anotherMethod',
                                            'main']), \
            "Wrong callable components extraction!"


def test_cpp_component_filler_helper(cpp_code_file):
    file_path, temp_dir_name = cpp_code_file
    parser = CppFileParser(file_path, temp_dir_name)

    helper = CppComponentFillerHelper("main", file_path, parser)

    code = helper.extract_component_code()
    assert "int main() {" in code
    assert helper.component_type == "function"
    assert 'std::cout << sc.greet() << std::endl;' in code

    to_link = helper.extract_callable_objects()
    assert set(to_link) == set([
        'SampleClass.sampleMethod', 'SampleClass.greet',
        'SampleClass.anotherMethod', 'std::cout'
    ])
