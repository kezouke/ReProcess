
def get_import_statement_path(file_path):
    # Split the path using '/' (or '\\' on Windows) to get the package names
    packages_with_extension = file_path.split('/')[1:] if '/' in file_path \
                                else file_path.rsplit('\\', 1)[1:]
    packages_with_extension = ".".join(packages_with_extension)
    packages = packages_with_extension.replace('.py', '')
    return packages