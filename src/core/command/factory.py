from typing import Type

from core.command.repository import CommandRepository
from core.command.types import Command


class CommandFactory:

    @staticmethod
    def get_command(name: str) -> [Type[Command], None]:
        for command_class in CommandRepository.LIST:
            if command_class.name() == name:
                return command_class

        return None
