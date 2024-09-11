import random
import tempfile
import pytest
import os
from reprocess.re_processors import JsonConverter, GraphBuilder, CloneRepository, Compose
from reprocess.re_container import ReContainer
from reprocess.utils.import_path_extractor import get_import_statement_path


# Utility to extract repository name from a git URL
def extract_repo_name(repo_url):
    return repo_url.split('/')[-1].replace('.git', '')


@pytest.fixture(scope="session")
def processed_repo():
    repo_list_path = os.path.join(os.path.dirname(__file__), 'repo_list.txt')

    # Load the repository list from the txt file
    with open(repo_list_path, 'r') as file:
        repos = file.readlines()

    # Randomly select a repository
    repo_url = random.choice(repos).strip()

    # Extract the repository name
    repo_name = extract_repo_name(repo_url)

    # Create a temporary directory for cloning the repository and storing results
    with tempfile.TemporaryDirectory(
    ) as temp_repo_dir, tempfile.TemporaryDirectory() as temp_output_dir:

        # Initialize the ReContainer with the repository name and temp directories
        repo_container = ReContainer(repo_name,
                                     os.path.join(temp_repo_dir, repo_name),
                                     temp_output_dir)

        # Define the Compose sequence of operations
        composition = Compose(
            [CloneRepository(repo_url),
             GraphBuilder(),
             JsonConverter()])

        # Run the Compose sequence on the repository container
        new_container = composition(repo_container)

        # Return the container for use in tests
        yield new_container


def test_code_fragment_presence(processed_repo):
    """
    This test checks if randomly selected code components are present 
    in their respective files within the cloned repository.

    Steps:
    1. Randomly select up to 50 code components from the repository.
    2. For each selected component:
       - Extract the relevant part of the component's name, excluding its file path.
       - Open the corresponding file.
       - Check if each part of the component's name is present in the file's code.
    """
    print("_" * 20)
    code_components = processed_repo.code_components
    files = {file.file_id: file for file in processed_repo.files}

    # Check if there are code components available
    if len(code_components) == 0:
        print("No code components found.")
        return

    # Determine the number of components to sample
    num_to_sample = min(50, len(code_components))
    sampled_components = random.sample(code_components, num_to_sample)

    # Process each sampled component
    for i, component in enumerate(sampled_components):
        print(f"Component {i + 1}: {component.component_name}")

        # Extract the file path without the extension
        file_path = ".".join(files[component.file_id].file_path.replace(
            "/", ".").split(".")[:-1]) + "."

        # Remove the file path part from the component name
        name_parts_to_check = component.component_name.replace(file_path,
                                                               "").split(".")

        # Open the corresponding file and read its content
        file_full_path = os.path.join(processed_repo.repo_path,
                                      files[component.file_id].file_path)
        with open(file_full_path, "r") as file:
            code = file.read()

            # Check if each part of the component's name is present in the code
            for part in name_parts_to_check:
                assert part in code, f"'{part}' not found in {file_full_path}"
    print("_" * 20)


def test_file_data_presence(processed_repo):
    """
    This test verifies that the import statements, called components,
    and callable components are present in the randomly selected files
    from the cloned repository.

    Steps:
    1. Randomly select up to 10 files from the repository.
    2. For each selected file:
       - Check if each import statement is present in the file.
       - Check if each called component is present in the file.
       - Check if each callable component is present in the file.
    """
    print("_" * 20)
    files = processed_repo.files

    # Determine the number of files to sample
    num_to_sample = min(10, len(files))
    sampled_files = random.sample(files, num_to_sample)

    # Process each sampled file
    for file in sampled_files:
        full_path = os.path.join(processed_repo.repo_path, file.file_path)

        print(f"file_path: {file.file_path};")
        print(f"len(imports): {len(file.imports)};")
        print(f"len(called_components): {len(file.called_components)};")
        print(f"len(callable_components: {len(file.callable_components)})")
        print()

        with open(full_path, "r") as f:
            code = f.read()

            # Check if each import statement is present in the code
            for import_statement in file.imports:
                assert import_statement in code, f"Import '{import_statement}' not found in {full_path}"

            # Check if each called component is present in the code
            for called_cmp in file.called_components:
                assert called_cmp in code, f"Called component '{called_cmp}' not found in {full_path}"

            # Check if each callable component is present in the code
            for callable_cmp in file.callable_components:
                assert callable_cmp in code, f"Callable component '{callable_cmp}' not found in {full_path}"
    print("_" * 20)


def test_component_linking(processed_repo):
    print("_" * 20)
    code_components = processed_repo.code_components
    files = {file.file_id: file for file in processed_repo.files}
    components_map = {cmp.component_id: cmp for cmp in code_components}

    # Check if there are code components available
    if len(code_components) == 0:
        print("No code components found.")
        return

    # Determine the number of components to sample
    num_to_sample = min(10, len(code_components))
    sampled_components = random.sample(code_components, num_to_sample)

    for component in sampled_components:
        if component.linked_component_ids:
            print(f"component: {component.component_name}")
            print(
                f"linked_components len: {len(component.linked_component_ids)}"
            )

            random_linked_cmp_id = random.choice(
                component.linked_component_ids)
            random_linked_cmp = components_map[random_linked_cmp_id]

            print(
                f"randomly chosed linked component: {random_linked_cmp.component_name}"
            )
            print()

            file_full_path = os.path.join(processed_repo.repo_path,
                                          files[component.file_id].file_path)

            with open(file_full_path, "r") as f:
                code = f.read()
                assert random_linked_cmp.component_name.split(".")[-1] in code, \
                        f"Linked component {random_linked_cmp.component_name} not found in file {file_full_path}"

            assert random_linked_cmp.component_name.split(".")[-1] in component.component_code, \
                    f"Linked component {random_linked_cmp.component_name} not found in component_code of {component.component_name}"

    print("_" * 20)
