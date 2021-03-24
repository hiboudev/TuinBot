from abc import abstractmethod
from enum import Enum
from typing import TypeVar, Generic, Optional

from discord import Message, Client

from core.param.params import CommandParam


class ParamResultType(Enum):
    VALID = 1
    INVALID = 2


ValidatedType = TypeVar('ValidatedType')


class CommandParamExecutor(Generic[ValidatedType]):

    TypeChecking = str

    def __init__(self, param: CommandParam):
        self.param = param
        self.__result_type = ParamResultType.INVALID
        self.__error = None
        self.__is_input_format_valid = False

    def set_value(self, value: str, message: Message, client: Client):
        validated_value = self._validate_input_format(value)
        if validated_value is None:
            return

        self.__is_input_format_valid = True

        for config in self.param.configs:
            if not config.validate(validated_value):
                self._set_error(f"**{self.param.name}** invalide : `{config.get_definition()}`.")
                return

        if self._process_param(validated_value, message, client):
            self.__result_type = ParamResultType.VALID

    @staticmethod
    @abstractmethod
    def always_validate_input_format() -> bool:
        """
        Indicate if this object will always accept input even if post-processing
        finds it's not valid.
        It's used to check if syntax is accepted as the "wanted" syntax by user, even if parameters contain errors.
        """
        pass

    @abstractmethod
    def _validate_input_format(self, value: str) -> Optional[ValidatedType]:
        pass

    @abstractmethod
    def _process_param(self, validated_value: ValidatedType, message: Message, client: Client) -> bool:
        pass

    def is_input_format_valid(self) -> bool:
        return self.__is_input_format_valid

    def get_result_type(self) -> ParamResultType:
        return self.__result_type

    def get_error(self) -> str:
        return self.__error

    def _set_error(self, error: str) -> bool:
        self.__error = error
        return False
