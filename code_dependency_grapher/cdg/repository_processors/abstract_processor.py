from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from abc import ABC, abstractmethod, ABCMeta
import ast
import inspect
import functools
import copy


class FunctionAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.container_name = "repository_container"
        self.used_attrs = set()
        self.assigned_attrs = set()

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == self.container_name:
            self.used_attrs.add(node.attr)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Attribute):
            self.assigned_attrs.add(node.targets[0].attr)
        self.generic_visit(node)

# def decorator(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         print(f"before calling: {func.__name__}")
#         result = func(*args, **kwargs)
#         print(f"after calling: {func.__name__}")
#         return result
#     return wrapper

class Meta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        cls._init_kwargs = kwargs
        if '__call__' in attrs:
            original_call = attrs['__call__']
            # print(inspect.getsource(original_call))
            # for name, method in inspect.getmembers(original_call, predicate=inspect.ismethod):
            source = inspect.getsource(original_call)
            lines = source.split('\n')
            first_line = lines[0]
            leading_spaces = len(first_line) - len(first_line.lstrip())
            normalized_source = '\n'.join(line[leading_spaces:] for line in lines)
            # print(normalized_source)
            tree = ast.parse(normalized_source)

            analyzer = FunctionAnalyzer()
            analyzer.visit(tree)
            # print(original_call.__code__.co_varnames)
            
            if 'repository_container' in original_call.__code__.co_varnames:
                param_index = original_call.__code__.co_varnames.index('repository_container')
                param_type = original_call.__annotations__.get('repository_container', None)
                if param_index == 1 and param_type == RepositoryContainer:
                    req_attrs_list = list(analyzer.assigned_attrs)
                    # print(f"Attributes used in method '{name}': {analyzer.used_attrs}")
                    # print(f"Attributes required in class '{name}': {analyzer.used_attrs.difference(analyzer.assigned_attrs)}")
                    # print(f"Attributes assigned in class '{name}': {req_attrs_list}")
                    



            @functools.wraps(original_call)
            def wrapped_call(self, repository_container, *args, **kwargs):
                # Perform the analysis before calling the original __call__ method
                
                original_container = copy.deepcopy(repository_container)
                result = original_call(self, repository_container,*args, **kwargs)
                active_container = repository_container if cls._init_kwargs.get('inplace') else copy.deepcopy(repository_container)
                
                print(original_container == active_container)

                for key, value in result.items():
                    setattr(active_container, key, value)
                return active_container
            
            setattr(cls, '__call__', wrapped_call)
            setattr(cls, "required_attrs", req_attrs_list)
        return cls
    




class CombinedMeta(ABCMeta, Meta):
    pass


class RepositoryProcessor(ABC, metaclass=CombinedMeta):
    def __new__(cls, *args, **kwargs):    
        cls._init_kwargs = kwargs
        return super().__new__(cls)


    @abstractmethod
    def __call__(self, repository_container: RepositoryContainer):
        pass