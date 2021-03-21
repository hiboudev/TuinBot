import asyncio
import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Type, Union, Iterable, Coroutine

from discord import Message, Client, Embed

from command.messages import HelpMessageBuilder, Messages
from command.params.executors import ParamExecutorFactory
from command.params.params import ParamType, ParamResultType
from command.params.syntax import CommandSyntax
from command.types import Command, HookType
from utils.utils import Utils


class BaseCommand(Command, ABC):
    _delete_delay = 10
    _delete_delay_help = 60

    _syntaxes = None
    _sorted_syntaxes = None
    _min_params_count = None
    _max_params_count = None

    def execute(self, message: Message, command_params: List[str], client: Client):
        if not command_params or not self.get_syntaxes():
            self._display_help(message)
            return

        syntaxes = self._get_sorted_syntaxes()

        if len(command_params) < self._min_params_count \
                or len(command_params) > self._max_params_count:
            self._display_error(message, "Nombre de paramètres inatendu !")
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

            for param in syntax.params:
                if param_index not in all_executors:
                    all_executors[param_index] = {}

                if param.param_type not in all_executors[param_index]:
                    executor = ParamExecutorFactory.get_executor(param)
                    executor.set_value(command_params[param_index], message, client)
                    all_executors[param_index][param.name] = executor
                else:
                    executor = all_executors[param_index][param.name]

                syntax_executors.append(executor)

                if not executor.always_valid_input_format():
                    if not executor.is_input_format_valid():
                        syntax_is_valid = False
                        break
                    elif executor.get_result_type() == ParamResultType.INVALID:
                        self._display_error(message, executor.get_error())
                        return
                else:
                    if executor.get_result_type() == ParamResultType.INVALID:
                        self._display_error(message, executor.get_error())
                        return

                param_index += 1

            if syntax_is_valid:
                syntax.callback(message, *syntax_executors)  # [:len(syntax.params)])
                return

        # No valid syntax, can we reach this?
        self._display_error(message, """Ha ! On dirait que le développeur n'avait pas prévu ça !
Merci de lui expliquer l'horreur que tu viens de faire pour qu'il corrige :wink:""")

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
            Utils.multisort(cls._sorted_syntaxes, (("always_valid_input_format", False), ("param_count", True)))

        return cls._sorted_syntaxes

    @classmethod
    @abstractmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        pass

    @classmethod
    def _display_error(cls, message: Message, error: str):
        cls._reply(message, "%s. Tape **!%s** pour afficher l'aide." % (error, cls.name()))

    @classmethod
    def _display_help(cls, message: Message):
        cls._reply(message, cls.get_help(), cls._delete_delay_help)

    @classmethod
    def _execute_db_bool_request(cls, func: Callable, message):
        result = func()
        if not result:
            cls._reply(message, Messages.nothing_to_do())

        return result

    @classmethod
    def _reply(cls, message: Message, content: Union[Embed, str], delete_delay: int = None):
        asyncio.create_task(cls._reply_and_delete(message, content, delete_delay))

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
        return HelpMessageBuilder(cls).build()


class Commands:
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

        return cls._hooks[hook_type]

    @classmethod
    def _validate_commands_syntax(cls, commands: Iterable[Type[Command]]):
        for command in commands:
            CommandSyntax.validate_syntaxes(command.get_syntaxes())
