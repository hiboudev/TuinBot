from abc import abstractmethod
from enum import Enum
from typing import Union, Dict, Type

from discord import Message, TextChannel, User, Client

from utils.parsing_utils import ParsingUtils


class ParamType(Enum):
    INVALID = 1
    USER = 2
    EMOJI = 3
    ALTERNATE_VALUE = 4


class CommandParam:

    def __init__(self, name: str, description: str, main_type: ParamType, alternate_value: str = None):
        self.name = name
        self.description = description
        self.main_type = main_type
        self.alternate_value = alternate_value


class ParamExpectedResult:

    def __init__(self, param: CommandParam, expected_result_type: ParamType):
        self.param = param
        self.expected_result_type = expected_result_type


class CommandParamExecutor:

    def __init__(self, param: CommandParam):
        self.param = param
        self._result_type = ParamType.INVALID
        self._error = None

    def set_value(self, value: str, message: Message, client: Client):
        if self.param.alternate_value is not None and self.param.alternate_value == value:
            self._result_type = ParamType.ALTERNATE_VALUE
        else:
            self._process_value(value, message, client)

    @abstractmethod
    def _process_value(self, value: str, message: Message, client: Client):
        """Process value only for the main type, alternate value has been processed in set_value."""
        pass

    def get_result_type(self) -> ParamType:
        return self._result_type

    def get_error(self) -> str:
        return self._error


class UserParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._user = None

    def _process_value(self, value: str, message: Message, client: Client):
        if not isinstance(message.channel, TextChannel):
            return

        # TODO ce serait bien de stocker les min/max sur le param,
        # mais comment bien gérer la doc selon si c'est un chiffre ou un string ?
        if len(value) < 3:
            self._error = "Le nom d'utilisateur doit faire au moins 3 caractères"
            return

        self._user = ParsingUtils.find_user(message.channel.members, value)

        if self._user:
            self._result_type = ParamType.USER
        else:
            self._error = "Utilisateur introuvable"

    def get_user(self) -> Union[User, None]:
        return self._user


class EmojiParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._emoji = None

    def _process_value(self, value: str, message: Message, client: Client):
        # if not isinstance(message.channel, TextChannel):
        #     return

        self._emoji = ParsingUtils.get_emoji(value, client)

        if self._emoji:
            self._result_type = ParamType.EMOJI
        else:
            self._error = "Emoji invalide"

    def get_emoji(self) -> Union[str, None]:
        return self._emoji


class ParamExecutorFactory:
    _executors_by_type: Dict[ParamType, Type[CommandParamExecutor]] = {
        ParamType.USER: UserParamExecutor,
        ParamType.EMOJI: EmojiParamExecutor
    }

    @classmethod
    def get_executor(cls, param: CommandParam) -> CommandParamExecutor:
        if param.main_type not in cls._executors_by_type:
            raise Exception("No param executor for this type!")

        return cls._executors_by_type[param.main_type](param)
