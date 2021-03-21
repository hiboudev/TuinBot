from typing import Type

from command.command_base import Commands
from command.types import Command


class CommandFactory:

    @staticmethod
    def get_command(name: str) -> [Type[Command], None]:
        for command_class in Commands.LIST:
            if command_class.name() == name:
                return command_class

        return None
