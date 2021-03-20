import asyncio
from abc import ABC
from typing import List, Dict, Callable, Type, Union

from discord import Message, Client, Embed

from command.messages import HelpMessageBuilder, Messages
from command.params.params import CommandParam, CommandParamExecutor, ParamExecutorFactory, ParamType
from command.types import Command, HookType


class BaseCommand(Command, ABC):
    _delete_delay = 10
    _delete_delay_help = 60

    def execute(self, message: Message, command_params: List[str], client: Client):
        if not command_params or not self.get_params():
            self._display_help(message)
            return

        params = self.get_params()
        executors: Dict[CommandParam, CommandParamExecutor] = {}
        param_index = 0

        for user_param in command_params[:len(params)]:
            param = params[param_index]
            executor = ParamExecutorFactory.get_executor(param)
            executor.set_value(user_param, message, client)

            if executor.get_result_type() == ParamType.INVALID:
                self._display_error(message, executor.get_error())
                return

            executors[param] = executor
            param_index += 1

        syntaxes = self.get_syntaxes()
        syntaxes.sort(key=lambda x: len(x.params), reverse=True)

        for syntax in syntaxes:
            if len(command_params) < len(syntax.params):
                continue

            syntax_is_valid = True

            for param in syntax.params:
                executor = executors[param.param]
                if param.expected_result_type != executor.get_result_type():
                    syntax_is_valid = False
                    break

            if syntax_is_valid:
                syntax.callback(message, *list(executors.values())[:len(syntax.params)])
                return

        # No valid syntax, can we reach this?

    @classmethod
    def _display_error(cls, message: Message, error: str):
        cls._reply(message, "%s. Tapez **!%s** pour afficher l'aide." % (error, cls.name()))

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

    @classmethod
    def get_help(cls) -> Union[Embed, str]:
        return HelpMessageBuilder(cls).build()


class Commands:
    _hooks: Dict = None

    # LIST = [TuinBotCommand, AutoReactionCommand]
    # List is not filled here cause of cyclic import issue.
    LIST = []

    # _hooks: Dict[HookType, Command] = None
    # cf. https://mypy.readthedocs.io/en/latest/generics.html#variance-of-generic-types
    # Command = TypeVar("Command", covariant=True)

    @classmethod
    def set_command_list(cls, *command_list: Type[Command]):
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
