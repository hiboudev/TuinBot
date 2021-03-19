from typing import Callable

from command.params.params import ParamExpectedResult


class CommandSyntax:

    def __init__(self, title: str, callback: Callable, *params: ParamExpectedResult):
        self.title = title
        self.params = params
        self.callback = callback

    # def is_valid(self) -> bool:
    #     for param in self._params:
    #         if param.param.get_result_type() != param.expected_result:
    #             return False
    #
    #     return True

    # def execute_callback(self):
    #     self._callback()
