from reprocess.parsers.python_parsers import PythonFileParser, PythonComponentFillerHelper

file_path = "/home/arxiv-feed/feed/database.py"
parser = PythonFileParser(file_path, "arxiv-feed")

print("Component Names:")
print(parser.extract_component_names())

print("\nImports:")
print(parser.extract_imports())

print("\nCalled components:")
print(parser.extract_called_components())

print("\nCallable components:")
print(parser.extract_callable_components())

helper = PythonComponentFillerHelper("feed.database.get_announce_papers",
                                     file_path, parser)
print("\nComponent Code:")
print(helper.extract_component_code())

print("\nComponent type:")
print(helper.component_type)

print("\nCallabale components")
print(helper.extract_callable_objects())

print("\nSignature:")
print(helper.extract_signature())
