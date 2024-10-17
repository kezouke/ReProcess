from .c_parsers import CComponentFillerHelper, CFileParser
from .cpp_parsers import CppComponentFillerHelper, CppFileParser
from .go_parsers import GoComponentFillerHelper, GoFileParser
from .java_parsers import JavaComponentFillerHelper, JavaFileParser
from .java_script_parsers import JavaScriptComponentFillerHelper, JavaScriptFileParser
from .python_parsers import PythonComponentFillerHelper, PythonFileParser
from .typescript_parser import TypeScriptComponentFillerHelper, TypeScriptFileParser

if __file__ == "__main__":
    c_file = CFileParser("", "")
    CComponentFillerHelper("", "", c_file)

    cpp_file = CppFileParser("", "")
    CppComponentFillerHelper("", "", cpp_file)

    go_file = GoFileParser("", "")
    GoComponentFillerHelper("", "", go_file)

    java_file = JavaFileParser("", "")
    JavaComponentFillerHelper("", "", java_file)

    js_file = JavaScriptFileParser("", "")
    JavaScriptComponentFillerHelper("", "", js_file)

    python_file = PythonFileParser("", "")
    PythonComponentFillerHelper("", "", python_file)

    ts_file = TypeScriptFileParser("", "")
    TypeScriptComponentFillerHelper("", "", ts_file)