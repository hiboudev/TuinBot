from typing import List, Dict, Type, Iterable

from core.command.types import Command, HookType
from core.param.validator import SyntaxValidator


class CommandRepository:
    _hooks: Dict[HookType, List[Type[Command]]] = None

    # List is not filled here cause of cyclic import issue.
    LIST: Iterable[Type[Command]] = []

    @classmethod
    def set_command_list(cls, *command_list: Type[Command]):
        cls._validate_commands_syntax(command_list)
        cls.LIST = command_list

    @classmethod
    def get_hooks(cls, hook_type: HookType) -> List[Type[Command]]:
        if cls._hooks is None:
            cls._hooks = {}
            for command in cls.LIST:
                if command.has_hook():
                    if command.hook_type() not in cls._hooks:
                        cls._hooks[command.hook_type()] = []
                    cls._hooks[command.hook_type()].append(command)

        if hook_type in cls._hooks:
            return cls._hooks[hook_type]

        return []

    @classmethod
    def _validate_commands_syntax(cls, commands: Iterable[Type[Command]]):
        for command in commands:
            SyntaxValidator.validate_syntaxes(command.get_syntaxes(), command.name())
