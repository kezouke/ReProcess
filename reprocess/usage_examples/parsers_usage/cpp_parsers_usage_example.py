from reprocess.parsers.cpp_parsers import CppFileParser, CppComponentFillerHelper


file_path = "/home/arxiv-feed/feed/test.cpp"
parser = CppFileParser(file_path, "your_repo_name")

print("Component Names:")
print(parser.extract_component_names())

print("\nCalled Components:")
print(parser.extract_called_components())

print("\nCallable Components:")
print(parser.extract_callable_components())

print("\nImports:")
print(parser.extract_imports())


helper = CppComponentFillerHelper("MyClass.anotherMethod", file_path, parser)
print()
print(helper.extract_component_code())
print(helper.extract_callable_objects())

print("\nSignature components")
print(helper.extract_signature())