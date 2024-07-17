import ast
from typing import List, Optional, Dict, Tuple
from uuid import UUID
from dataclasses import dataclass
from reprocess.utils.import_path_extractor import get_import_statement_path
from reprocess.utils.mappers.file_path_ast_mapper import FilePathAstMapError
from reprocess.utils.mappers.id_component_mapper import IdComponentMapError
from reprocess.utils.mappers.id_file_analyzer_mapper import IdFileAnalyzerMapper, IdFileAnalyzeMapError


@dataclass
class CodeComponentContainer:
    """
    Represents a container for a single code component (function or class) within a Python file.
    
    Attributes:
        component_id (str): Unique identifier for the component.
        component_name (str): Name of the component.
        component_code (str): Source code of the component.
        linked_component_ids (List[str]): IDs of components this component is linked to.
        file_id (str): Identifier for the file containing the component.
        external_component_ids (List[str]): IDs of external components referenced by this component.
    """

    def __init__(self, component_id: str, component_name: str,
                 component_code: str, linked_component_ids: List[str],
                 file_id: str, external_component_ids: List[str],
                 component_type: str) -> None:
        """
        Initializes a new instance of the CodeComponentContainer class.
        
        Parameters:
            component_id (str): Unique identifier for the component.
            component_name (str): Name of the component.
            component_code (str): Source code of the component.
            linked_component_ids (List[str]): IDs of components this component is linked to.
            file_id (str): Identifier for the file containing the component.
            external_component_ids (List[str]): IDs of external components referenced by this component.
            component_type (str): Whether component is class, method or function

        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_code = component_code
        self.linked_component_ids = linked_component_ids
        self.file_id = file_id
        self.external_component_ids = external_component_ids
        self.component_type = component_type

    def getComponentAttribute(self, attribute_name):
        """
        Retrieves the value of an attribute from the component container.
        
        Parameters:
            attribute_name (str): Name of the attribute to retrieve.
            
        Returns:
            Any: Value of the requested attribute, or None if the attribute does not exist.
        """
        return getattr(self, attribute_name, None)

    def setComponentAttribute(self, attribute_name, value):
        """
        Sets the value of an attribute in the component container.
        
        Parameters:
            attribute_name (str): Name of the attribute to set.
            value: New value for the attribute.
        """
        setattr(self, attribute_name, value)

    def extract_imports(self):
        """
        Extracts and returns a list of import statements used by the component.
        
        Returns:
            List[str]: A list of import statements.
        """
        tree = ast.parse(self.component_code)
        imports = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    imports.append(module_name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    module_name = node.module
                    component_name = alias.name
                    imports.append(f"{module_name}.{component_name}")

        return imports

    def __eq__(self, other) -> bool:
        if isinstance(other, CodeComponentContainer):
            self_attrs = vars(self)
            other_attrs = vars(other)

            if self_attrs.keys() != other_attrs.keys():
                return False

            for key in self_attrs.keys():
                if key not in other_attrs or self_attrs[key] != other_attrs[
                        key]:
                    return False
            return True
        else:
            return False