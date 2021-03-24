import asyncio
import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Union, Coroutine

from discord import Message, Client, Embed

from core.command.types import Command
from core.executor.base import ParamResultType
from core.executor.factory import ParamExecutorFactory
from core.message.messages import Messages
from core.param.syntax import CommandSyntax
from core.utils.utils import Utils


class BaseCommand(Command, ABC):
    _delete_delay = 10
    _delete_delay_help = 40

    _syntaxes = None
    _sorted_syntaxes = None
    _min_params_count = None
    _max_params_count = None

    @classmethod
    def execute(cls, message: Message, command_params: List[str], client: Client):
        if not command_params or not cls.get_syntaxes():
            cls._display_help(message)
            return

        syntaxes = cls._get_sorted_syntaxes()

        if len(command_params) < cls._min_params_count or len(command_params) > cls._max_params_count:
            cls._display_error(message, "Nombre de paramètres inatendu !")
            return

        """ Stores one executor by parameter index and parameter name,
        so we parse each parameter only once.
        """
        all_executors: Dict[int, Dict[str]] = {}

        for syntax in syntaxes:
            if len(command_params) != len(syntax.params):
                continue

            syntax_executors = []
            syntax_is_valid = True
            param_index = 0
            executor = None

            for param in syntax.params:
                if param_index not in all_executors:
                    all_executors[param_index] = {}

                if param.name not in all_executors[param_index]:
                    executor = ParamExecutorFactory.get_executor(param)
                    all_executors[param_index][param.name] = executor
                    executor.set_value(command_params[param_index], message, client)
                else:
                    executor = all_executors[param_index][param.name]

                syntax_executors.append(executor)

                if not executor.always_validate_input_format():
                    if not executor.is_input_format_valid():
                        syntax_is_valid = False
                        break
                    elif executor.get_result_type() == ParamResultType.INVALID:
                        cls._display_error(message, executor.get_error())
                        return
                else:
                    if executor.get_result_type() == ParamResultType.INVALID:
                        cls._display_error(message, executor.get_error())
                        return

                param_index += 1

            if syntax_is_valid:
                syntax.callback(message, *syntax_executors)  # [:len(syntax.params)])
                return
            elif executor:
                # TODO voir comment afficher l'erreur, quand aucun param n'a validé l'entrée
                print(executor.param.name)

        # No valid syntax nor giving error, can we reach this?
        cls._display_error(message, """Tu as dû faire une petite erreur quelque part.""")

    @classmethod
    def get_syntaxes(cls) -> List[CommandSyntax]:
        if cls._syntaxes is None:
            cls._syntaxes = cls._build_syntaxes()

            cls._min_params_count = sys.maxsize
            cls._max_params_count = 0

            for syntax in cls._syntaxes:
                if syntax.param_count < cls._min_params_count:
                    cls._min_params_count = syntax.param_count

                if syntax.param_count > cls._max_params_count:
                    cls._max_params_count = syntax.param_count

        return cls._syntaxes

    @classmethod
    def _get_sorted_syntaxes(cls) -> List[CommandSyntax]:
        if cls._sorted_syntaxes is None:
            cls._sorted_syntaxes = cls.get_syntaxes().copy()
            Utils.multisort(cls._sorted_syntaxes, (("always_validate_input_format", False), ("param_count", True)))

        return cls._sorted_syntaxes

    @classmethod
    @abstractmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        pass

    @classmethod
    def _display_error(cls, message: Message, error: str):
        cls._reply(message, "%s Tape **!%s** pour afficher l'aide." % (error, cls.name()))

    @classmethod
    def _display_help(cls, message: Message):
        cls._reply(message, cls.get_help(), cls._delete_delay_help)

    @classmethod
    def _execute_db_bool_request(cls, func: Callable, message):
        result = func()
        if not result:
            cls._reply(message, Messages.nothing_to_do)

        return result

    @classmethod
    def _reply(cls, message: Message, content: Union[Embed, str], delete_delay: int = None):
        cls._async(cls._reply_and_delete(message, content, delete_delay))

    @classmethod
    async def _reply_and_delete(cls, message: Message, content: Union[Embed, str], delay: int = None):
        if isinstance(content, Embed):
            response = await message.reply(embed=content)
        else:
            response = await message.reply(content=content)

        await response.delete(delay=delay or cls._delete_delay)
        await message.delete(delay=delay or cls._delete_delay)

    @staticmethod
    def _async(coro: Coroutine):
        asyncio.create_task(coro)

    @classmethod
    def get_help(cls) -> Union[Embed, str]:
        return Messages.build_help(cls)
