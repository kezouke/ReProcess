from reprocess.parsers.java_script_parsers import JavaScriptFileParser, JavaScriptComponentFillerHelper

file_path = "/home/arxiv-feed/feed/test.js"
parser = JavaScriptFileParser(file_path, "arxiv-feed")

print("Component Names:")
print(parser.extract_component_names())

print("\nCalled Components:")
print(parser.extract_called_components())

print("\nImports:")
print(parser.extract_imports())

print("\nCallable Components:")
print(parser.extract_callable_components())

helper = JavaScriptComponentFillerHelper("feed.test.createAndLogProperties",
                                         file_path, parser)
print("\nComponent Code:")
print(helper.extract_component_code())

print("\nCallabale components")
print(helper.extract_callable_objects())
