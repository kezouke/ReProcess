import pytest
import tempfile
import os

from reprocess.parsers import JavaScriptFileParser, JavaScriptComponentFillerHelper


@pytest.fixture(scope='session')
def javascript_code_file():
    """
    Fixture to generate a JavaScript code file with classes, variables, functions, and methods,
    write it to a temporary file, and return the path to the file and the temporary folder name.
    """
    # Sample JavaScript code to be written to the file
    javascript_code = r"""
class User {
    constructor(name) {
        this.name = name;
    }

    greet() {
        return `Hello, ${this.name}!`;
    }

    static createAdmin() {
        return new User("Admin");
    }

    static logRole(role) {
        console.log(`User role is ${role}`);
    }
}

const DEFAULT_USER = new User("Guest");

function greetUser(user) {
    console.log(user.greet());
}

const someVariable = 42;
"""

    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'GeneratedCode.js')

        # Write the JavaScript code to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(javascript_code)

        # Return the path and directory name
        yield temp_file_path, os.path.basename(temp_dir)


def test_javascript_file_parser(javascript_code_file):
    file_path, temp_dir_name = javascript_code_file
    parser = JavaScriptFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['GeneratedCode.User',
                                    'GeneratedCode.User.constructor',
                                    'GeneratedCode.User.greet',
                                    'GeneratedCode.User.createAdmin',
                                    'GeneratedCode.User.logRole',
                                    'GeneratedCode.DEFAULT_USER',
                                    'GeneratedCode.greetUser',
                                    'GeneratedCode.someVariable']), \
            "Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(['user.greet', 'console.log', 'GeneratedCode.User']), \
            "Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['GeneratedCode.User',
                                            'GeneratedCode.User.constructor',
                                            'GeneratedCode.User.greet',
                                            'GeneratedCode.User.createAdmin',
                                            'GeneratedCode.User.logRole',
                                            'GeneratedCode.DEFAULT_USER',
                                            'GeneratedCode.greetUser',
                                            'GeneratedCode.someVariable']), \
            "Wrong callable components extraction!"


def test_javascript_component_filler_helper(javascript_code_file):
    file_path, temp_dir_name = javascript_code_file
    parser = JavaScriptFileParser(file_path, temp_dir_name)

    helper = JavaScriptComponentFillerHelper("GeneratedCode.User.createAdmin",
                                             file_path, parser)

    code = helper.extract_component_code()
    assert "static createAdmin()" in code
    assert helper.component_type == "method"
    assert "return new User(\"Admin\");" in code

    to_link = helper.extract_callable_objects()
    assert set(to_link) == set()
