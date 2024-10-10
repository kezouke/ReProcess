import pytest
import tempfile
import os

from reprocess.parsers import TypeScriptFileParser, TypeScriptComponentFillerHelper


@pytest.fixture(scope='session')
def typescript_code_file():
    """
    Fixture to generate a TypeScript code file with classes, variables, enums, and functions,
    write it to a temporary file, and return the path to the file and the temporary folder name.
    """
    # Sample TypeScript code to be written to the file
    typescript_code = r"""
export enum UserRole {
    Admin,
    User,
    Guest
}

export class User {

    constructor(name: string) {
        this.name = name;
    }

    greet(): string {
        return `Hello, ${this.name}!`;
    }

    static createAdmin(): User {
        return new User("Admin");
    }

    static logRole(role: UserRole): void {
        console.log(`User role is ${role}`);
    }
}

export const DEFAULT_USER = new User("Guest");

function greetUser(user: User): void {
    console.log(user.greet());
}
"""

    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'GeneratedCode.ts')

        # Write the TypeScript code to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(typescript_code)

        # Return the path and directory name
        yield temp_file_path, os.path.basename(temp_dir)


def test_typescript_file_parser(typescript_code_file):
    file_path, temp_dir_name = typescript_code_file
    parser = TypeScriptFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['GeneratedCode.User',
                                  'GeneratedCode.User.greet',
                                  'GeneratedCode.User.constructor',
                                  'GeneratedCode.User.createAdmin',
                                  'GeneratedCode.User.logRole',
                                  'GeneratedCode.DEFAULT_USER',
                                  'GeneratedCode.greetUser',
                                  'GeneratedCode.UserRole']), \
            "Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(['user.greet',
                                          'console.log',
                                          'GeneratedCode.User']), \
            "Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['GeneratedCode.User',
                                            'GeneratedCode.User.constructor',
                                            'GeneratedCode.User.greet',
                                            'GeneratedCode.User.createAdmin',
                                            'GeneratedCode.User.logRole',
                                            'GeneratedCode.DEFAULT_USER',
                                            'GeneratedCode.greetUser',
                                            'GeneratedCode.UserRole']), \
            "Wrong callable components extraction!"


def test_typescript_component_filler_helper(typescript_code_file):
    file_path, temp_dir_name = typescript_code_file
    parser = TypeScriptFileParser(file_path, temp_dir_name)

    helper = TypeScriptComponentFillerHelper("GeneratedCode.User.createAdmin",
                                             file_path, parser)

    code = helper.extract_component_code()
    assert "static createAdmin(): User" in code
    assert "return new User(\"Admin\");" in code

    to_link = helper.extract_callable_objects()
    assert set(to_link) == set(
        ['GeneratedCode.User.createAdmin', 'GeneratedCode.User'])
