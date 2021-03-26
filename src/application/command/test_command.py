from typing import List

from discord import Message, User

from application.database.db_spoiler import DbAutoSpoiler
from application.message.messages import AppMessages
from application.param.app_params import ApplicationParams
from core.command.base import BaseCommand
from core.command.types import HookType
from core.executor.base import CommandParamExecutor
from core.executor.executors import UserParamExecutor, FixedValueParamExecutor
from core.param.syntax import CommandSyntax
from core.utils.parsing_utils import ParsingUtils


class TestCommand(BaseCommand):

    @staticmethod
    def name() -> str:
        return "test"

    @staticmethod
    def description() -> str:
        return "test"

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:

        syntaxes = [
            CommandSyntax("test",
                          cls._test1,
                          ApplicationParams.SENTENCE
                          ),
        ]

        return syntaxes

    @classmethod
    def _test1(cls, message: Message, exec1: CommandParamExecutor):
        print(exec1)
