from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union

from discord import Message, Client, Embed, TextChannel, Member

from command.params.syntax import CommandSyntax


class HookType(Enum):
    NONE = 1
    TYPING = 2
    MESSAGE = 3


class Command(ABC):

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def description() -> str:
        pass

    @classmethod
    @abstractmethod
    def get_syntaxes(cls) -> List[CommandSyntax]:
        pass

    @classmethod
    @abstractmethod
    def execute(cls, message: Message, command_params: List[str], client: Client):
        pass

    @classmethod
    @abstractmethod
    def get_help(cls) -> Union[Embed, str]:
        pass

    @staticmethod
    def has_hook() -> bool:
        return False

    @staticmethod
    def hook_type() -> HookType:
        return HookType.NONE

    @classmethod
    def execute_hook(cls, message: Message = None, typing_channel: TextChannel = None, typing_user: Member = None):
        pass
