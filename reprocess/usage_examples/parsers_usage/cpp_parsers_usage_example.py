from reprocess.parsers.cpp_parsers import CppFileParser, CppComponentFillerHelper

file_path = "/home/guidance/guidance/_cpp/byte_trie.cpp"
parser = CppFileParser(file_path, "guidance")

print("Component Names:")
print(parser.extract_component_names())

print("\nCalled Components:")
print(parser.extract_called_components())

print("\nCallable Components:")
print(parser.extract_callable_components())

print("\nImports:")
print(parser.extract_imports())

helper = CppComponentFillerHelper("ByteTrie.keys", file_path, parser)
print()
print(f'code:{helper.extract_component_code()}')
print(f'callable:{helper.extract_callable_objects()}')
