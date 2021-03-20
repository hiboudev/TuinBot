from abc import abstractmethod
from enum import Enum
from typing import Union, Dict, Type

from discord import Message, TextChannel, User, Client

from utils.parsing_utils import ParsingUtils


class ParamType(Enum):
    USER = 1
    EMOJI = 2
    SINGLE_VALUE = 3


class ParamResultType(Enum):
    VALID = 1
    INVALID = 2


class CommandParam:

    def __init__(self, name: str, description: str, param_type: ParamType, single_value: str = None):
        if param_type == ParamType.SINGLE_VALUE and single_value is None \
                or param_type != ParamType.SINGLE_VALUE and single_value is not None:
            raise Exception("param_type and single_value are not coherents!")

        self.name = name
        self.description = description
        self.param_type = param_type
        self.single_value = single_value


class CommandParamExecutor:

    def __init__(self, param: CommandParam):
        self.param = param
        self._result_type = ParamResultType.INVALID
        self._error = None
        self._is_input_format_valid = False

    @abstractmethod
    def set_value(self, value: str, message: Message, client: Client):
        pass

    @staticmethod
    @abstractmethod
    def always_valid_input_format() -> bool:
        """
        Indicate if this object will always accept input even if post-processing
        finds it's not valid.
        It's used to check if syntax is accepted as the "wanted" syntax by user, even if parameters contain errors.
        """
        pass

    def is_input_format_valid(self) -> bool:
        return self._is_input_format_valid

    def get_result_type(self) -> ParamResultType:
        return self._result_type

    def get_error(self) -> str:
        return self._error


class UserParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._user = None

    def set_value(self, value: str, message: Message, client: Client):
        print(self)
        if not isinstance(message.channel, TextChannel):
            return

        # TODO ce serait bien de stocker les min/max sur le param,
        # mais comment bien gérer la doc selon si c'est un chiffre ou un string ?
        if len(value) < 3:
            self._error = "Le nom d'utilisateur doit faire au moins 3 caractères"
            return

        self._user = ParsingUtils.find_user(message.channel.members, value)

        if self._user:
            self._result_type = ParamResultType.VALID
        else:
            self._error = "Utilisateur introuvable"

    def get_user(self) -> Union[User, None]:
        return self._user

    @staticmethod
    def always_valid_input_format() -> bool:
        return True

    def is_input_format_valid(self) -> bool:
        return True


class EmojiParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._emoji = None

    def set_value(self, value: str, message: Message, client: Client):
        print(self)

        self._emoji = ParsingUtils.get_emoji(value, client)

        if self._emoji:
            self._result_type = ParamResultType.VALID
        else:
            self._error = "Emoji invalide"

    def get_emoji(self) -> Union[str, None]:
        return self._emoji

    @staticmethod
    def always_valid_input_format() -> bool:
        return True

    def is_input_format_valid(self) -> bool:
        return True


class SingleValueParamExecutor(CommandParamExecutor):

    def set_value(self, value: str, message: Message, client: Client):
        print(self)
        if value == self.param.single_value:
            self._is_input_format_valid = True
            self._result_type = ParamResultType.VALID
        else:
            self._error = "Valeur invalide"

    @staticmethod
    def always_valid_input_format() -> bool:
        return False


class ParamExecutorFactory:
    _executors_by_type: Dict[ParamType, Type[CommandParamExecutor]] = {
        ParamType.USER: UserParamExecutor,
        ParamType.EMOJI: EmojiParamExecutor,
        ParamType.SINGLE_VALUE: SingleValueParamExecutor
    }

    @classmethod
    def get_executor(cls, param: CommandParam) -> CommandParamExecutor:
        if param.param_type not in cls._executors_by_type:
            raise Exception("No param executor for this type!")

        return cls._executors_by_type[param.param_type](param)

    @classmethod
    def get_executor_class(cls, param: CommandParam) -> Type[CommandParamExecutor]:
        if param.param_type not in cls._executors_by_type:
            raise Exception("No param executor for this type!")

        return cls._executors_by_type[param.param_type]
