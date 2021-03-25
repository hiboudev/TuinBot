from abc import abstractmethod, ABC
from enum import Enum
# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import Generic, TypeVar, Union, _GenericAlias, Type, get_args, List


class ParamType(Enum):
    USER = 1
    EMOJI = 2
    FIXED_VALUE = 3
    INT = 4
    TEXT = 5


SupportedType = TypeVar('SupportedType')


class ParamConfig(ABC, Generic[SupportedType]):

    def __init__(self):
        self.__error = None

    def validate(self, value: SupportedType) -> bool:
        # We could type check value at runtime to ensure executor gave us
        # the good type, but SyntaxValidator.validate_syntaxes() should be enough.

        return self._validate(value)

    @staticmethod
    @abstractmethod
    def is_input_validator() -> bool:
        """Return True if this config can invalidate input,
        so we can jump to next syntax if config doesn't validate."""
        pass

    @abstractmethod
    def get_definition(self) -> str:
        pass

    @abstractmethod
    def _validate(self, value: SupportedType) -> bool:
        pass

    def _set_error(self, error: str) -> bool:
        self.__error = error
        return False


class NumberMinMaxParamConfig(ParamConfig[Union[int, float]]):

    def __init__(self, min_value: int = None, max_value: int = None):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value

        if self.min_value is None and self.max_value is None:
            raise ValueError("One of both parameters must be set!")

    @staticmethod
    def is_input_validator() -> bool:
        return False

    def get_definition(self) -> str:
        if self.min_value is not None and self.max_value is not None:
            return f"entre {self.min_value} et {self.max_value} inclus"
        elif self.min_value is not None:
            return f"minimum {self.min_value}"
        elif self.max_value is not None:
            return f"maximum {self.min_value}"
        return ""

    def _validate(self, value: SupportedType) -> bool:
        if self.min_value is not None and self.min_value > value:
            return False
        if self.max_value is not None and self.max_value < value:
            return False

        return True


class TextMinMaxParamConfig(ParamConfig[str]):

    def __init__(self, min_length: int = None, max_length: int = None):
        super().__init__()
        self.min_length = min_length
        self.max_length = max_length

        if self.min_length is None and self.max_length is None:
            raise ValueError("One of both parameters must be set!")

    @staticmethod
    def is_input_validator() -> bool:
        return False

    def get_definition(self) -> str:
        if self.min_length is not None and self.max_length is not None:
            return f"entre {self.min_length} et {self.max_length} caractères"
        elif self.min_length is not None:
            return f"minimum {self.min_length} caractères"
        elif self.max_length is not None:
            return f"maximum {self.min_length} caractères"
        return ""

    def _validate(self, value: SupportedType) -> bool:
        value_len = len(value)

        if self.min_length is not None and value_len < self.min_length:
            return False
        if self.max_length is not None and value_len > self.max_length:
            return False

        return True


class ListParamConfig(ParamConfig[str]):

    def __init__(self, *values: str):
        super().__init__()
        self.values = values

    @staticmethod
    def is_input_validator() -> bool:
        return True

    def get_definition(self) -> str:
        return "valeurs possibles : [{}]".format(", ".join(self.values))

    def _validate(self, value: SupportedType) -> bool:
        return value in self.values


class CommandParam:

    def __init__(self, name: str, description: str, param_type: ParamType, *configs: ParamConfig):
        self.name = name
        self.description = description
        self.param_type = param_type
        self.configs = configs
