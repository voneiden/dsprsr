import functools
from dataclasses import dataclass, field
from typing import Callable, Any


class empty:
    pass


class StopChain(Exception):
    def __init__(self, final_value):
        super().__init__(final_value)
        self.final_value = final_value


class ListValidationError(Exception):
    pass


@dataclass
class Chain:
    chain: list = field(default_factory=list)

    def __rshift__(self, other):
        return Chain(chain=self.chain + other.chain)

    def resolve(self, source_data, variables):
        resolved_data = source_data
        for i, link in enumerate(self.chain):
            try:
                resolved_data = link.resolve(resolved_data, variables)
            except StopChain as ex:
                return ex.final_value

            except Exception as ex:
                print(f"MagicChain failed to resolve at {'->'.join([repr(_link) for _link in self.chain[0:i+1]])}")
                raise ex
        return resolved_data


@dataclass
class Value:
    """ Magic Object, serves also as a base class """
    key: str
    default: Any = field(default_factory=lambda: empty)

    def __new__(cls, *args, **kwargs):
        obj = super(Value, cls).__new__(cls)
        # noinspection PyArgumentList
        obj.__init__(*args, **kwargs)

        return Chain(chain=[obj])

    def resolve(self, o, _):
        v = o.get(self.key, self.default)
        if v is None:
            raise StopChain(None)
        if v == empty:
            raise KeyError(f'{self.key} (available {o.items()})')
        return v

@dataclass
class List:
    """ Magic List """
    key: str
    cast: bool = False
    index: int = None
    min_length: int = None
    max_length: int = None
    reduce: tuple[Callable, Callable] = None
    filter: Callable = None
    default: Any = field(default_factory=lambda: empty)

    def __new__(cls, *args, **kwargs):
        obj = super(List, cls).__new__(cls)
        # noinspection PyArgumentList
        obj.__init__(*args, **kwargs)

        return Chain(chain=[obj])

    def resolve(self, source_data, _):
        v = source_data.get(self.key, self.default)
        if v is None:
            raise StopChain(None)
        if self.cast and not isinstance(v, list):
            v = [v]
        if self.max_length is not None and len(v) > self.max_length:
            raise ListValidationError(f"List ({self.key}) violates max_length ({len(v)})")
        if self.min_length is not None and  len(v) < self.min_length:
            raise ListValidationError(f"List ({self.key}) violates min_length")

        if self.reduce is not None:
            f, default_factory = self.reduce
            v = functools.reduce(f, v, default_factory())

        if self.filter is not None:
            v = list(filter(self.filter, v))

        if self.index is not None:
            return v[self.index]

        return v


@dataclass
class Variable:
    name: str

    def __new__(cls, *args, **kwargs):
        obj = super(Variable, cls).__new__(cls)
        # noinspection PyArgumentList
        obj.__init__(*args, **kwargs)

        return Chain(chain=[obj])

    def resolve(self, source_data, variables):
        return variables[self.name].resolve(source_data, variables)

@dataclass
class Schema:
    schema: [dict, list]
    variables: dict = None

    def __new__(cls, *args, **kwargs):
        obj = super(Schema, cls).__new__(cls)
        # noinspection PyArgumentList
        obj.__init__(*args, **kwargs)

        return Chain(chain=[obj])

    def resolve(self, source_data, variables):
        def _magic_map(_source_data):
            return magic_map(self.schema, _source_data, {**variables, **(self.variables if self.variables else {})})
        if isinstance(source_data, list):
            return [_magic_map(_source_data) for _source_data in source_data]
        return _magic_map(source_data)


def magic_map(schema, source_data, variables: dict = None):
    if not variables:
        variables = {}

    if isinstance(schema, dict):
        return {k: magic_map(v, source_data, variables) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [magic_map(v, source_data, variables) for v in schema]
    elif isinstance(schema, Chain):
        return schema.resolve(source_data, variables=variables)
