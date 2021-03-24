# Ne pas enlever, je pige pas trop l'erreur, import cyclique ?
from __future__ import annotations

from typing import Callable

from discord import Message

from core.executor.base import CommandParamExecutor
from core.executor.factory import ParamExecutorFactory
from core.param.params import CommandParam


class CommandSyntax:

    def __init__(self, title: str, callback: Callable[[Message, *CommandParamExecutor], None],
                 *params: CommandParam):
        self.title = title
        self.params = params
        self.callback = callback
        self._always_validate_input_format = None

    @property
    def param_count(self) -> int:
        return len(self.params)

    @property
    def always_validate_input_format(self) -> bool:
        # TODO devrait être ailleurs, mais sert pour le tri...
        if self._always_validate_input_format is None:
            for param in self.params:
                if not ParamExecutorFactory.get_executor_class(param.param_type).always_validate_input_format():
                    self._always_validate_input_format = False
                    return False
            self._always_validate_input_format = True

        return self._always_validate_input_format
