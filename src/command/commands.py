from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Callable, Type, Union

from discord import Message, Client, Embed

from command.params.params import CommandParam, CommandParamExecutor, ParamExecutorFactory, ParamType, \
    ParamExpectedResult, UserParamExecutor, EmojiParamExecutor
from command.params.syntax import CommandSyntax
from database.database import Database


class HookType(Enum):
    NONE = 1
    TYPING = 2
    MESSAGE = 3


class Command(ABC):
    _delete_delay = 10
    _delete_delay_help = 60

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def description_short() -> str:
        pass

    @classmethod
    @abstractmethod
    def get_params(cls) -> List[CommandParam]:
        pass

    @classmethod
    @abstractmethod
    def get_syntaxes(cls) -> List[CommandSyntax]:
        pass

    @staticmethod
    def has_hook() -> bool:
        return False

    @staticmethod
    def hook_type() -> HookType:
        return HookType.NONE

    @classmethod
    def execute_hook(cls, message: Message):
        pass

    def execute(self, message: Message, command_params: List[str], client: Client):
        if not command_params:
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


class TuinBotCommand(Command):

    @staticmethod
    def name() -> str:
        return "tuin"

    @staticmethod
    def description_short() -> str:
        return "Affiche les commandes disponibles pour les tuins."

    @classmethod
    def get_params(cls) -> List[CommandParam]:
        return []

    @classmethod
    def get_syntaxes(cls) -> List[CommandSyntax]:
        return []

    @classmethod
    def get_help(cls) -> str:
        help_mess = "Commandes disponibles :"

        for command in Commands.LIST:
            help_mess += "\n**!%s** : %s" % (command.name(), command.description_short())
        help_mess += "\nTape une commande pour voir sa page d'aide."

        return help_mess


class AutoReactionCommand(Command):
    _params = None
    _syntaxes = None

    def __init__(self):
        self.user_executor = None

    @staticmethod
    def name() -> str:
        return "reac"

    @staticmethod
    def description_short() -> str:
        return "Ajoute une réaction automatique aux messages d'un tuin."

    @classmethod
    def get_params(cls) -> List[CommandParam]:
        if cls._params is None:
            cls._params = [
                CommandParam("tuin", "Le nom ou une partie du nom du tuin.", ParamType.USER, "stop"),
                CommandParam("emoji", "Un emoji qui lui collera au cul pour un moment.", ParamType.EMOJI, "stop"),
            ]

        return cls._params

    @classmethod
    def get_syntaxes(cls) -> List[CommandSyntax]:
        params = cls.get_params()

        if cls._syntaxes is None:
            cls._syntaxes = [
                CommandSyntax("Ajoute une réaction sur un tuin",
                              cls._add_reaction,
                              ParamExpectedResult(params[0], ParamType.USER),
                              ParamExpectedResult(params[1], ParamType.EMOJI)
                              ),
                CommandSyntax("Enlève ta réaction sur un tuin",
                              cls._remove_reaction,
                              ParamExpectedResult(params[0], ParamType.USER),
                              ParamExpectedResult(params[1], ParamType.ALTERNATE_VALUE)
                              ),
                CommandSyntax("Liste les réactions mises sur un tuin",
                              cls._list_reactions,
                              ParamExpectedResult(params[0], ParamType.USER)
                              ),
                CommandSyntax("Enlève toutes les réactions que les sales tuins t'ont mis",
                              cls._remove_all_reactions,
                              ParamExpectedResult(params[0], ParamType.ALTERNATE_VALUE)
                              )
            ]

        return cls._syntaxes

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.MESSAGE

    @classmethod
    def execute_hook(cls, message: Message):
        reactions = Database().get_auto_reactions(message.author.id)

        for reaction in reactions:
            asyncio.create_task(message.add_reaction(reaction))

    @classmethod
    def _add_reaction(cls, message: Message, user_executor: UserParamExecutor, emoji_executor: EmojiParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        Database.add_auto_reaction(message.author.id,
                                                                   user_executor.get_user().id,
                                                                   emoji_executor.get_emoji()
                                                                   ),
                                        message):
            cls._reply(message,
                       "Réaction automatique %s ajoutée à %s !" % (
                           emoji_executor.get_emoji(), user_executor.get_user().name))

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_reaction(cls, message: Message, user_executor: UserParamExecutor, emoji_executor: EmojiParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        Database.remove_auto_reaction(message.author.id, user_executor.get_user().id),
                                        message):
            cls._reply(message, "Réaction automatique retirée de %s !" % user_executor.get_user().name)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_all_reactions(cls, message: Message, user_executor: UserParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        Database().remove_all_auto_reactions(message.author.id),
                                        message):
            cls._reply(message, "OK, j'ai viré les réactions automatiques que ces sales tuins t'avaient mises !")

    @classmethod
    def _list_reactions(cls, message: Message, user_executor: UserParamExecutor):
        reactions = Database().get_auto_reactions(user_executor.get_user().id)
        cls._reply(message,
                   "%s a %s réaction(s) automatique(s) : %s" % (
                       user_executor.get_user().name, len(reactions), " ".join(reactions)))


class Commands:
    LIST = [TuinBotCommand, AutoReactionCommand]
    _hooks: Dict = None

    # _hooks: Dict[HookType, Command] = None
    # cf. https://mypy.readthedocs.io/en/latest/generics.html#variance-of-generic-types
    # Command = TypeVar("Command", covariant=True)

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


class Messages:
    @staticmethod
    def nothing_to_do() -> str:
        return "Il n'y a rien à faire."


class HelpMessageBuilder:

    def __init__(self, command: Type[Command]):
        self._command = command

    def build(self) -> Embed:
        embed = Embed(title="Commande __{name}__".format(name=self._command.name()),
                      description="*%s*" % self._command.description_short())

        field_count = 0

        for syntax in self._command.get_syntaxes():
            params_syntax = []
            params_desc = []

            for param in syntax.params:
                param_is_variable = param.expected_result_type != ParamType.ALTERNATE_VALUE
                param_display_name = ("[%s]" if param_is_variable else "%s") % param.param.name

                params_syntax.append(param_display_name)

                if param_is_variable:
                    params_desc.append("**%s** : %s" % (param_display_name, param.param.description))

            embed.add_field(name=syntax.title, inline=True,
                            value="""```ini\n!{name} {params}```{desc}""".format(
                                name=self._command.name(),
                                params=" ".join(params_syntax),
                                desc="\n".join(params_desc))
                            )

            field_count += 1

            if field_count % 2 == 1:
                embed.add_field(name="\u200B", value="\u200B", inline=True)

            if field_count % 2 == 0 and field_count < len(self._command.get_syntaxes()):
                embed.add_field(name="\u200B", value="\u200B", inline=False)

        return embed
