from reprocess.re_container import ReContainer
from reprocess.utils.attribute_linker import get_attribute_linker
from abc import ABC, abstractmethod, ABCMeta
import ast
import inspect
import functools
import copy
import os
import aiohttp


class FunctionAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.container_name = "repository_container"
        self.used_attrs = set()
        self.assigned_attrs = set()

    def visit_Attribute(self, node):
        if isinstance(node.value,
                      ast.Name) and node.value.id == self.container_name:
            self.used_attrs.add(node.attr)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Attribute):
            self.assigned_attrs.add(node.targets[0].attr)
        self.generic_visit(node)


def find_return_attributes(source_code):
    tree = ast.parse(source_code)
    return_statements = [
        node for node in ast.walk(tree) if isinstance(node, ast.Return)
    ]

    returned_attrs = set()
    for ret in return_statements:
        values = ret.value
        if 'keys' in vars(values):
            for key in values.keys:
                returned_attrs.add(key.value)
    return list(returned_attrs)


class AbsentAttributesException(Exception):

    def __init__(self, absent_list, cls_name, *args):
        super().__init__(args)
        self.absent_list = absent_list
        self.cls_name = cls_name

    def __str__(self):
        attribute_linker = get_attribute_linker()
        formatted_attrs = [f"`{attr}`" for attr in self.absent_list]
        answer_string = f"\nAbsent attributes during execution of {self.cls_name}: {', '.join(formatted_attrs)}\n"

        attr_cls_map = attribute_linker.get_classes_by_attrs(self.absent_list)
        attr_strings = []

        for attr, classes in attr_cls_map.items():
            attr_strings.append(f"To assign `{attr}`, refer to:\n" +
                                ",\n".join(classes))

        answer_string += "\n\n".join(attr_strings)
        return answer_string


class Meta(type):

    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        cls._init_kwargs = kwargs
        if '__call__' in attrs:

            # prepare code for the parsing
            original_call = attrs['__call__']
            source = inspect.getsource(original_call)
            lines = source.split('\n')
            first_line = lines[0]
            leading_spaces = len(first_line) - len(first_line.lstrip())
            normalized_source = '\n'.join(line[leading_spaces:]
                                          for line in lines)
            tree = ast.parse(normalized_source)

            analyzer = FunctionAnalyzer()
            analyzer.visit(tree)

            if 'repository_container' in original_call.__code__.co_varnames:
                param_index = original_call.__code__.co_varnames.index(
                    'repository_container')
                param_type = original_call.__annotations__.get(
                    'repository_container', None)
                if param_index == 1 and param_type == ReContainer:
                    req_attrs_list = list(analyzer.used_attrs)

            req_attrs_list = list(
                filter(lambda x: x[:2] != "__", req_attrs_list))
            return_attrs = find_return_attributes(normalized_source)
            attribute_linker = get_attribute_linker()
            attribute_linker(name, return_attrs)

            # rewriten call method
            @functools.wraps(original_call)
            def wrapped_call(self, repository_container, *args, **kwargs):
                # assert that all the required attributes are given
                absent_attrs = []
                existing_attrs = vars(repository_container).keys()
                for attr in self.required_attrs:
                    if attr not in existing_attrs:
                        absent_attrs.append(attr)
                if absent_attrs:
                    raise AbsentAttributesException(absent_attrs, name)

                original_container = copy.deepcopy(repository_container)
                result = original_call(self, repository_container, *args,
                                       **kwargs)
                assert isinstance(
                    result, dict
                ), "You should return dict with updated attributes and their values"
                assert original_container == repository_container, f"You should not explicitly modify repository container inside the {name}"

                active_container = repository_container if cls._init_kwargs.get(
                    'inplace') else copy.deepcopy(repository_container)

                # update repository container attributes
                for key, value in result.items():
                    setattr(active_container, key, value)

                return active_container

            setattr(cls, '__call__', wrapped_call)
            setattr(cls, "required_attrs", req_attrs_list)
        return cls


class AsyncMeta(type):

    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs)
        cls._init_kwargs = kwargs
        if '__call__' in attrs:

            # prepare code for the parsing
            original_call = attrs['__call__']
            source = inspect.getsource(original_call)
            lines = source.split('\n')
            first_line = lines[0]
            leading_spaces = len(first_line) - len(first_line.lstrip())
            normalized_source = '\n'.join(line[leading_spaces:]
                                          for line in lines)
            tree = ast.parse(normalized_source)

            analyzer = FunctionAnalyzer()
            analyzer.visit(tree)

            if 'repository_container' in original_call.__code__.co_varnames:
                param_index = original_call.__code__.co_varnames.index(
                    'repository_container')
                param_type = original_call.__annotations__.get(
                    'repository_container', None)
                if param_index == 1 and param_type == ReContainer:
                    req_attrs_list = list(analyzer.used_attrs)

            req_attrs_list = list(
                filter(lambda x: x[:2] != "__", req_attrs_list))
            return_attrs = find_return_attributes(normalized_source)
            attribute_linker = get_attribute_linker()
            attribute_linker(name, return_attrs)

            # rewritten call method
            @functools.wraps(original_call)
            async def wrapped_call(self, repository_container, *args,
                                   **kwargs):
                # assert that all the required attributes are given
                absent_attrs = []
                existing_attrs = vars(repository_container).keys()
                for attr in self.required_attrs:
                    if attr not in existing_attrs:
                        absent_attrs.append(attr)
                if absent_attrs:
                    raise AbsentAttributesException(absent_attrs, name)

                original_container = copy.deepcopy(repository_container)
                result = await original_call(self, repository_container, *args,
                                             **kwargs)

                assert isinstance(
                    result, dict
                ), "You should return dict with updated attributes and their values"
                assert original_container == repository_container, f"You should not explicitly modify repository container inside the {name}"

                active_container = repository_container if cls._init_kwargs.get(
                    'inplace') else copy.deepcopy(repository_container)

                # update repository container attributes
                for key, value in result.items():
                    setattr(active_container, key, value)

                return active_container

            setattr(cls, '__call__', wrapped_call)
            setattr(cls, "required_attrs", req_attrs_list)
        return cls


class CombinedMeta(ABCMeta, Meta):
    pass


class AsyncCombinedMeta(ABCMeta, AsyncMeta):
    pass


class ReProcessor(ABC, metaclass=CombinedMeta):

    def __new__(cls, *args, **kwargs):
        cls._init_kwargs = kwargs
        return super().__new__(cls)

    @abstractmethod
    def __call__(self, repository_container: ReContainer):
        pass


class AsyncReProcessor(ABC, metaclass=AsyncCombinedMeta):

    def __new__(cls, *args, **kwargs):
        cls._init_kwargs = kwargs
        return super().__new__(cls)

    @abstractmethod
    async def __call__(self, repository_container: ReContainer):
        pass


class AsyncVLLMReProcessor(ABC, metaclass=AsyncCombinedMeta):

    class LLM:

        def __init__(self) -> None:
            self.url = os.getenv('LLM_URL')
            if not self.url:
                raise ValueError("Environment variable LLM_URL is not set")

        async def get_response(self, json_data):
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=json_data) as response:
                    if response.status != 200:
                        raise Exception(f"Error: {response.status}")
                    return await response.json()

        def __new__(cls, *args, **kwargs):
            cls._init_kwargs = kwargs
            cls.llm = AsyncVLLMReProcessor.LLM()
            return super().__new__(cls)

        @abstractmethod
        async def __call__(self, repository_container: ReContainer):
            pass
