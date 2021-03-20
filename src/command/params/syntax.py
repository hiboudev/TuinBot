from __future__ import annotations

from typing import Callable, List

from command.params.executors import ParamExecutorFactory
from command.params.params import CommandParam


class CommandSyntax:

    def __init__(self, title: str, callback: Callable, *params: CommandParam):
        self.title = title
        self.params = params
        self.callback = callback
        self._always_valid_input_format = None

    @property
    def param_count(self) -> int:
        return len(self.params)

    @property
    def always_valid_input_format(self) -> bool:
        if self._always_valid_input_format is None:
            for param in self.params:
                if not ParamExecutorFactory.get_executor_class(param).always_valid_input_format():
                    self._always_valid_input_format = False
                    return False
            self._always_valid_input_format = True

        return self._always_valid_input_format

    @staticmethod
    def validate_syntaxes(syntaxes: List[CommandSyntax]):
        always_valid_param_count = set()
        for syntax in syntaxes:
            if syntax.always_valid_input_format:
                if syntax.param_count in always_valid_param_count:
                    raise Exception("One of the command syntaxes will never execute!")
                always_valid_param_count.add(syntax.param_count)
