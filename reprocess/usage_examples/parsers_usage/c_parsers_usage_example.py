from reprocess.parsers.c_parsers import CFileParser, CComponentFillerHelper

file_path = "/home/arxiv-feed/feed/test.c"
parser = CFileParser(file_path, "aes")

print("Component Names:")
print(parser.extract_component_names())

print("\nCalled Components:")
print(parser.extract_called_components())

print("\nCallable Components:")
print(parser.extract_callable_components())

print("\nImports:")
print(parser.extract_imports())

helper = CComponentFillerHelper("myFunction", file_path, parser)
print(helper.extract_component_code())
print()
print(helper.extract_callable_objects())

print("\nSignature components")
print(helper.extract_signature())