from abc import abstractmethod
from enum import Enum

from discord import Message, Client

from core.param.params import CommandParam


class ParamResultType(Enum):
    VALID = 1
    INVALID = 2


class CommandParamExecutor:

    def __init__(self, param: CommandParam):
        self.param = param
        self.__result_type = ParamResultType.INVALID
        self.__error = None
        self.__is_input_format_valid = False

    def set_value(self, value: str, message: Message, client: Client):
        if not self._validate_input_format(value):
            return
        else:
            self.__is_input_format_valid = True

        if self._process_param(value, message, client):
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
    def _validate_input_format(self, value: str) -> bool:
        pass

    @abstractmethod
    def _process_param(self, value: str, message: Message, client: Client) -> bool:
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
