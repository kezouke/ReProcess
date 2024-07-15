from abc import ABC, abstractmethod

class TreeSitterComponentsFinder(ABC):
    def __init__(self,
                 file_path: str) -> None:
        self.file_path = file_path

        try:
            import tree_sitter
            import tree_sitter_languages
        except ImportError:
            raise ImportError(
                "Could not import tree_sitter/tree_sitter_languages Python packages. "
                "Please install them with "
                "`pip install tree-sitter tree-sitter-languages`."
            )
        
    @abstractmethod
    def extract_component_names(self):
        raise NotImplementedError()
    
    @abstractmethod
    def extract_imports(self):
        raise NotImplementedError()
    
    @abstractmethod
    def extract_called_components(self):
        raise NotImplementedError()
    
    @abstractmethod
    def extract_callable_components(self):
        raise NotImplementedError()


class TreeSitterComponentFillerHelper(ABC):

    def __init__(self,
                 component_name: str,
                 component_file_path: str) -> None:
        try:
            import tree_sitter
            import tree_sitter_languages
        except ImportError:
            raise ImportError(
                "Could not import tree_sitter/tree_sitter_languages Python packages. "
                "Please install them with "
                "`pip install tree-sitter tree-sitter-languages`."
            )
        
    
    @abstractmethod
    def extract_component_code(self):
        raise NotImplementedError()