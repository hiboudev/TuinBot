from abc import abstractmethod, ABC
from enum import Enum
# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import Generic, TypeVar, Union, _GenericAlias, Type


class ParamType(Enum):
    USER = 1
    EMOJI = 2
    FIXED_VALUE = 3
    INT = 4
    TEXT = 5


ValueType = TypeVar('ValueType')


class ParamConfig(ABC, Generic[ValueType]):

    def __init__(self):
        self.__error = None

    def validate(self, value: ValueType) -> bool:
        refering_type = self._get_type_checking()

        if isinstance(refering_type, _GenericAlias):
            # noinspection PyUnresolvedReferences
            refering_type = refering_type.__args__

        if not isinstance(value, refering_type):
            raise ValueError(
                f"Value of param {self.__class__.__name__} must be of type {refering_type}!")

        return self._validate(value)

    @abstractmethod
    def get_definition(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def _get_type_checking() -> Type:
        """Return the same type as the Generic used.
        Cause I'd like to check at runtime that we get the good type,
        and in the base class so we're quiet for sub-classing.
        But I didn't find how to use the Generic[Type] for that purpose."""
        return object

    @abstractmethod
    def _validate(self, value: ValueType) -> bool:
        pass

    def _set_error(self, error: str) -> bool:
        self.__error = error
        return False


class IntParamConfig(ParamConfig[int]):

    def __init__(self, min_value: int = None, max_value: int = None):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value

        if self.min_value is None and self.max_value is None:
            raise ValueError("One of both parameters must be set!")

    def get_definition(self) -> str:
        if self.min_value is not None and self.max_value is not None:
            return f"entre {self.min_value} et {self.max_value} inclus"
        elif self.min_value is not None:
            return f"minimum {self.min_value}"
        elif self.max_value is not None:
            return f"maximum {self.min_value}"
        return ""

    @staticmethod
    def _get_type_checking() -> Type:
        return int

    def _validate(self, value: ValueType) -> bool:
        return self.min_value <= value <= self.max_value


class CommandParam:

    def __init__(self, name: str, description: str, param_type: ParamType, *configs: ParamConfig):
        self.name = name
        self.description = description
        self.param_type = param_type
        self.configs = configs
