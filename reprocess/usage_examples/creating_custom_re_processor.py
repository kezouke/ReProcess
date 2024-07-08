# Import necessary classes and exceptions from the reprocess package
from reprocess.re_processors.processor import ReProcessor, AbsentAttributesException
from reprocess.re_container import ReContainer
from reprocess.re_processors import Compose


# Define a custom ReProcessorA class that extends the ReProcessor class
class ReProcessorA(ReProcessor):

    def __call__(self, repository_container: ReContainer):
        # Return a dictionary with the attribute 'attr_a' set to 10
        return {"attr_a": 10}


# Define a custom ReProcessorB class that extends the ReProcessor class
class ReProcessorB(ReProcessor):

    def __call__(self, repository_container: ReContainer):
        # Access the 'attr_a' attribute from the repository container
        attr_a = repository_container.attr_a
        # Calculate 'attr_b' as 'attr_a' multiplied by 10
        attr_b = attr_a * 10
        # Return a dictionary with the attribute 'attr_b'
        return {"attr_b": attr_b}


# Create an example repository container with specific paths
re_container_example = ReContainer("test_1", "/test_1", "/db")

# Instantiate the custom ReProcessors
a = ReProcessorA()
b = ReProcessorB()

# Separator for clarity
print("_" * 10)
print("Trying to access an undefined ReContainer attribute example:")

# Create a composition with only ReProcessorB
composition_example_1 = Compose([b])

# Attempt to run the composition and catch any AbsentAttributesException
try:
    new_container = composition_example_1(re_container_example)
except AbsentAttributesException as e:
    print(f"An error occurred: {e}")
'''
Expected output:
__________
Trying to access an undefined ReContainer attribute example:
An error occurred: 
Absent attributes during execution of ReProcessorB: `attr_a`
To assign `attr_a`, refer to:
ReProcessorA
__________
'''

# Separator for clarity
print("_" * 10)
print()
print("Using the hints we obtained above, run the correct pipeline:")

# Create a composition with both ReProcessorA and ReProcessorB
composition_example_2 = Compose([a, b])

# Run the composition to process the repository container
new_container = composition_example_2(re_container_example)

# Print the attributes of the new container
print(new_container.__dict__)
'''
Expected output:
{'repo_name': 'test_1',
 'repo_path': '/test_1', 
 'db_path': '/db', 
 'attr_a': 10, 
 'attr_b': 100}
'''
