from reprocess.parsers.go_parsers import GoFileParser

file_path = "/home/arxiv-feed/feed/test.go"
parser = GoFileParser(file_path, "arxiv-feed")

print("Component Names:")
print(parser.extract_component_names())