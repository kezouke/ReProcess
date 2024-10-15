from reprocess.re_processors.processor import ReProcessor
from reprocess.re_container import ReContainer
from neo4j import GraphDatabase


class Neo4jConverter(ReProcessor):
    """
    A class that processes a repository container and saves its data into Neo4j.
    
    This class inherits from ReProcessor and overrides the `process` method 
    to store the repository's components and files into a Neo4j graph database. 
    It creates nodes for code components and files, and establishes relationships
    between them based on their links.
    """

    def __init__(self, uri, user, password, **kwargs):
        """
        Initializes the Neo4jConverter with the connection details for the Neo4j database.
        
        :param uri: The URI of the Neo4j database.
        :param user: The username for Neo4j authentication.
        :param password: The password for Neo4j authentication.
        """
        if uri:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_code_component(self, tx, component):
        """
        Creates a node for a code component in the Neo4j database.
        
        :param tx: The transaction object.
        :param component: A dictionary representing the code component.
        """
        tx.run("""
            MERGE (c:CodeComponent {component_id: $component_id})
            ON CREATE SET c.name = $component_name,
                          c.code = $component_code,
                          c.type = $component_type
            """,
               component_id=component.component_id,
               component_name=component.component_name,
               component_code=component.component_code,
               component_type=component.component_type)

    def create_file(self, tx, file):
        """
        Creates a node for a file in the Neo4j database.
        
        :param tx: The transaction object.
        :param file: A dictionary representing the file.
        """
        tx.run("""
            MERGE (f:File {file_id: $file_id})
            ON CREATE SET f.path = $file_path,
                          f.imports = $imports,
                          f.called_components = $called_components,
                          f.callable_components = $callable_components
            """,
               file_id=file.file_id,
               file_path=file.file_path,
               imports=file.imports,
               called_components=file.called_components,
               callable_components=file.callable_components)

    def create_relationship(self, tx, source_id, target_id, source_type,
                            target_type, relationship_type):
        """
        Creates a relationship between two nodes in the Neo4j database.
        
        :param tx: The transaction object.
        :param source_id: The ID of the source node.
        :param target_id: The ID of the target node.
        :param source_type: The type of the source node ('CodeComponent' or 'File').
        :param target_type: The type of the target node ('CodeComponent' or 'File').
        :param relationship_type: The type of relationship (e.g., 'uses', 'inside').
        """
        # Determine the property for matching based on the node type
        source_property = "component_id" if source_type == "CodeComponent" else "file_id"
        target_property = "component_id" if target_type == "CodeComponent" else "file_id"

        tx.run(f"""
            MATCH (a {{{source_property}: $source_id}}), (b {{{target_property}: $target_id}})
            MERGE (a)-[r:{relationship_type}]->(b)
            """,
               source_id=source_id,
               target_id=target_id)

    def __call__(self, repository_container: ReContainer):
        """
        Processes the given repository container and saves its data into the Neo4j database.
        
        :param repository_container: An instance of ReContainer containing the repository's data.
        """
        # Start a session with Neo4j
        with self.driver.session(database="neo4j") as session:
            # Store code components
            for component in repository_container.code_components:
                session.write_transaction(self.create_code_component,
                                          component)

            # Store files
            for file in repository_container.files:
                session.write_transaction(self.create_file, file)

            # Create relationships between code components (linked components)
            for component in repository_container.code_components:
                for linked_id in component.linked_component_ids:
                    session.write_transaction(self.create_relationship,
                                              component.component_id,
                                              linked_id, "CodeComponent",
                                              "CodeComponent", "USES")
                session.write_transaction(self.create_relationship,
                                          component.file_id,
                                          component.component_id, "File",
                                          "CodeComponent", "INSIDE")

        self.close()
        return {"is_saved_to_neo4j": True}
