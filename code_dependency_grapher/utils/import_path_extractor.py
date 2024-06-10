def get_import_statement_path(file_path: str) -> str:
    """
    Extracts the package path from a given file path, suitable for use in an import statement.
    
    This function splits the file path to isolate the package hierarchy leading up to the file, excluding the file extension. It then joins these segments with dots ('.') to form a string that represents the package path. This path can be used in Python import statements to refer to the file's location within the project structure.
    
    Args:
        file_path (str): The full path to the file from which to extract the package path.
    
    Returns:
        str: The package path extracted from the file path, formatted for use in import statements.
    """
    # Split the path using '/' (or '\\' on Windows) to get the package names
    # Adjusting for Windows path style by splitting from rightmost occurrence of '\\'
    packages_with_extension = file_path.split('/')[1:] if '/' in file_path \
                                else file_path.rsplit('\\', 1)[1:]
    # Join the package names with dots ('.') to form the package path
    packages_with_extension = ".".join(packages_with_extension)
    # Remove the '.py' extension from the package path
    packages = packages_with_extension.replace('.py', '')
    return packages
