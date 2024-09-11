import pytest
import tempfile
import os
from reprocess.parsers.python_parsers import PythonFileParser, PythonComponentFillerHelper


@pytest.fixture(scope='session')
def python_code_file():
    """
    Fixture to generate a Python code file with classes, methods, and functions,
    write it to a temporary file, and return the path to the file.
    """
    
    # Sample Python code to be written to the file
    python_code = r"""
import random
    
class SampleClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f'Hello, {self.name}!'

def sample_function(x, y):
    sample_function()
    random.random()
    return x + y

def another_function(a):
    if a > 10:
        return a * 2
    else:
        return a - 2

if __name__ == "__main__":
    sc = SampleClass('World')
    print(sc.greet())
    print(sample_function(5, 7))
    print(another_function(15))
    """
    
    # Create a temporary file and write the Python code to it
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'generated_code.py')

        with open(temp_file_path, 'w') as file:
            file.write(python_code)
        
        yield temp_file_path, os.path.basename(temp_dir)


def test_file_parser(python_code_file):
    file_path, temp_dir_name = python_code_file
    parser = PythonFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['generated_code.SampleClass', 
                         'generated_code.SampleClass.__init__', 
                         'generated_code.SampleClass.greet', 
                         'generated_code.sample_function', 
                         'generated_code.another_function']), \
            f"Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(['another_function', 
                                 'print', 
                                 'random', 
                                 'greet', 
                                 'SampleClass', 
                                 'sample_function']), \
            f"Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['SampleClass', 
                                            'another_function', 
                                            'sample_function']), \
            f"Wrong callable components extraction!"


    imports = parser.extract_imports()
    assert set(imports) == set(['random']), \
           f"Wrong imports extraction!"