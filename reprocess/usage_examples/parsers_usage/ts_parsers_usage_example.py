from reprocess.parsers.typescript_parser import TypeScriptFileParser, TypeScriptComponentFillerHelper

file_path = "/home/arxiv-feed/feed/vars.ts"
parser = TypeScriptFileParser(file_path, "arxiv-feed")

print("Component Names:")
print(parser.extract_component_names())

print("\nImports:")
print(parser.extract_imports())

print("\nCalled components:")
print(parser.extract_called_components())

print("\nCallable components:")
print(parser.extract_callable_components())

helper = TypeScriptComponentFillerHelper("feed.vars.changeUser", file_path,
                                         parser)
print("\nComponent Code:")
print(helper.extract_component_code())

print("\nComponent type:")
print(helper.component_type)

print("\nCallabale components")
print(helper.extract_callable_objects())
