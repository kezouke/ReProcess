import pytest
import tempfile
import os

from reprocess.parsers import JavaFileParser, JavaComponentFillerHelper


@pytest.fixture(scope='session')
def java_code_file():
    """
    Fixture to generate a Java code file with classes, methods, and functions,
    write it to a temporary file, and return the path to the file and the temporary folder name.
    """
    # Sample Java code to be written to the file
    java_code = r"""
public class SampleClass {
    private String name;

    public SampleClass(String name) {
        this.name = name;
    }

    public String greet() {
        return "Hello, " + name + "!";
    }
    
    public static void sampleMethod(int x, int y) {
        System.out.println("Sample method called with x=" + x + " and y=" + y);
    }

    public int anotherMethod(int a) {
        if (a > 10) {
            return a * 2;
        } else {
            return a - 2;
        }
    }

    public static void main(String[] args) {
        SampleClass sc = new SampleClass("World");
        System.out.println(sc.greet());
        sampleMethod(5, 7);
        System.out.println(sc.anotherMethod(15));
    }
}
"""

    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'GeneratedCode.java')

        # Write the Java code to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(java_code)

        # Return the path and directory name
        yield temp_file_path, os.path.basename(temp_dir)


def test_java_file_parser(java_code_file):
    file_path, temp_dir_name = java_code_file
    parser = JavaFileParser(file_path, temp_dir_name)

    cmp_names = parser.extract_component_names()
    assert set(cmp_names) == set(['GeneratedCode.java.SampleClass',
                                  'GeneratedCode.java.SampleClass.greet',
                                  'GeneratedCode.java.SampleClass.sampleMethod',
                                  'GeneratedCode.java.SampleClass.anotherMethod',
                                  'GeneratedCode.java.SampleClass.main']), \
            "Wrong component names extraction!"

    called_components = parser.extract_called_components()
    assert set(called_components) == set(['GeneratedCode.java.SampleClass.anotherMethod',
                                          'GeneratedCode.java.SampleClass',
                                          'GeneratedCode.java.SampleClass.sampleMethod',
                                          'System.out.println',
                                          'GeneratedCode.java.SampleClass.greet']), \
            "Wrong called components extraction!"

    callable_components = parser.extract_callable_components()
    assert set(callable_components) == set(['GeneratedCode.java.SampleClass',
                                            'GeneratedCode.java.SampleClass.greet',
                                            'GeneratedCode.java.SampleClass.sampleMethod',
                                            'GeneratedCode.java.SampleClass.anotherMethod',
                                            'GeneratedCode.java.SampleClass.main']), \
            "Wrong callable components extraction!"


def test_java_component_filler_helper(java_code_file):
    file_path, temp_dir_name = java_code_file
    parser = JavaFileParser(file_path, temp_dir_name)

    helper = JavaComponentFillerHelper(
        "GeneratedCode.java.SampleClass.sampleMethod", file_path, parser)

    code = helper.extract_component_code()
    assert "void sampleMethod(int x, int y)" in code
    assert helper.component_type == "method"
    assert "System.out.println(\"Sample method called with x=\" + x + \" and y=\" + y);" in code

    to_link = helper.extract_callable_objects()
    assert set(to_link) == set(['System.out.println'])
