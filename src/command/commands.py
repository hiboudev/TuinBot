from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Callable, Type, Union

from discord import Message, Client, User, Embed

from database.database import Database
from utils.parsing_utils import ParsingUtils


class HookType(Enum):
    NONE = 1
    TYPING = 2
    MESSAGE = 3


class Command(ABC):
    _delete_delay = 5
    _delete_delay_help = 60

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def description_short() -> str:
        pass

    # @staticmethod
    # @abstractmethod
    # def params_syntax() -> str:
    #     pass
    #
    # @staticmethod
    # @abstractmethod
    # def description_long() -> str:
    #     pass

    @classmethod
    @abstractmethod
    def _execute(cls, message: Message, command_params: List[str], bot: Client):
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

    @classmethod
    def execute(cls, message: Message, command_params: List[str], client: Client):
        if not command_params:
            cls._display_help(message)
        else:
            cls._execute(message, command_params, client)

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

    # @staticmethod
    # @abstractmethod
    # def params_syntax() -> str:
    #     return ""
    #
    # @staticmethod
    # @abstractmethod
    # def description_long() -> str:
    #     return ""

    @classmethod
    def _execute(cls, message: Message, command_params: List[str], bot: Client):
        # In case use calls it with parameters, show help.
        cls._display_help(message)

    @classmethod
    def get_help(cls) -> str:
        help_mess = "Commandes disponibles :"

        for command in Commands.LIST:
            help_mess += "\n**!%s** : %s" % (command.name(), command.description_short())
        help_mess += "\nTape une commande pour voir sa page d'aide."

        return help_mess

    # TODO def description : pour l'aide générale et individuelle


class AutoReactionCommand(Command):

    @staticmethod
    def name() -> str:
        return "reac"

    @staticmethod
    def description_short() -> str:
        return "Ajoute une réaction automatique aux messages d'un tuin."

    # @staticmethod
    # @abstractmethod
    # def params_syntax() -> str:
    #     return "tuin emoji"
    #
    # @staticmethod
    # @abstractmethod
    # def description_long() -> str:
    #     return """__tuin__ : Le nom ou une partie du nom du tuin.
    #     __emoji__ : Un emoji qui lui collera au cul pour un moment."""

    @classmethod
    def _execute(cls, message: Message, command_params: List[str], client: Client):
        num_parans = len(command_params)

        if num_parans < 1:
            cls._display_error(message, "Nombre de paramètres incorrect")
            return

        """ TODO
        * utilisateur peut être une mention
        """

        # Param 1 : "stop"
        if command_params[0] == "stop":
            cls._remove_all_reactions(message.author, message)
            return

        # Param 1 : User
        user = ParsingUtils.find_user(message.channel.members, command_params[0])
        if not user:
            cls._display_error(message, "Utilisateur introuvable")
            return

        # Param 2 missing
        if len(command_params) == 1:
            cls._list_reactions(user, message)
            return

        # Param 2 : "stop"
        if command_params[1] == "stop":
            cls._remove_reaction(user, message)
            return

        # Param 2 : Emoji (add reaction)
        emoji_param = command_params[1]
        emoji = ParsingUtils.get_emoji(emoji_param, client)
        if not emoji:
            cls._display_error(message, "Emoji introuvable")
            return

        cls._add_reaction(user, emoji, message)

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
    def _add_reaction(cls, user: User, emoji: str, message: Message):
        if cls._execute_db_bool_request(lambda:
                                        Database.add_auto_reaction(message.author.id, user.id, emoji),
                                        message):
            cls._reply(message, "Réaction automatique %s ajoutée à %s !" % (emoji, user.name))

    @classmethod
    def _remove_reaction(cls, user: User, message: Message):
        if cls._execute_db_bool_request(lambda:
                                        Database.remove_auto_reaction(message.author.id, user.id),
                                        message):
            cls._reply(message, "Réaction automatique retirée de %s !" % user.name)

    @classmethod
    def _remove_all_reactions(cls, user: User, message: Message):
        if cls._execute_db_bool_request(lambda:
                                        Database().remove_all_auto_reactions(user.id),
                                        message):
            cls._reply(message, "OK, j'ai viré les réactions automatiques que ces sales tuins t'avaient mises !")

    @classmethod
    def _list_reactions(cls, user: User, message: Message):
        reactions = Database().get_auto_reactions(user.id)
        cls._reply(message,
                   "%s a %s réaction(s) automatique(s) : %s" % (user.name, len(reactions), " ".join(reactions)))

    @classmethod
    def get_help(cls) -> Union[Embed, str]:
        return HelpMessageBuilder(cls).add_syntax(
            "Ajoute une réaction à un tuin",
            [CommandParam("tuin", "Le nom ou une partie du nom du tuin."),
             CommandParam("emoji", "Un emoji qui lui collera au cul pour un moment.")]
        ).add_syntax(
            "Enlève la réaction à un tuin",
            [CommandParam("tuin", "Le nom ou une partie du nom du tuin."),
             CommandParam("stop", "Juste \"stop\".", False)]
        ).add_syntax(
            "Retire toutes les réactions que les sales tuins t'ont mis",
            [CommandParam("stop", "Juste \"stop\".", False)]
        ).add_syntax(
            "Liste les réactions mises sur un tuin",
            [CommandParam("tuin", "Le nom ou une partie du nom du tuin.")]
        ).build()


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

    # @staticmethod
    # def help_message(command: Type[Command]) -> Embed:
    #     return Embed(title="Commande __{name}__".format(name=command.name()),
    #                  description=command.description_short()) \
    #         .add_field(name="Syntaxe",
    #                    value="""```apache\n!{name} {params}```{desc_long}""".format(
    #                        name=command.name(),
    #                        params=command.params_syntax(),
    #                        desc_long=command.description_long())
    #                    )


class CommandSyntax:

    def __init__(self, title: str, params: List[CommandParam]):
        self.title = title
        self.params = params


class CommandParam:

    def __init__(self, name: str, description: str, is_variable: bool = True):
        self.name = name
        self.description = description
        self.is_variable = is_variable


class HelpMessageBuilder:

    def __init__(self, command: Type[Command]):
        self.command = command
        self.syntaxes: List[CommandSyntax] = []

    def add_syntax(self, title: str, params: List[CommandParam]) -> HelpMessageBuilder:
        self.syntaxes.append(CommandSyntax(title, params))
        return self

    def build(self) -> Embed:
        embed = Embed(title="Commande __{name}__".format(name=self.command.name()),
                      description="*%s*" % self.command.description_short())

        # embed.add_field(name="\u200B", value="\u200B", inline=False)

        field_count = 0

        for syntax in self.syntaxes:
            params_syntax = []
            params_desc = []

            for param in syntax.params:
                param_display_name = ("[%s]" if param.is_variable else "%s") % param.name

                params_syntax.append(param_display_name)
                if param.is_variable:
                    params_desc.append("**%s** : %s" % (param_display_name, param.description))

            embed.add_field(name=syntax.title, inline=True,
                            value="""```ini\n!{name} {params}```{desc}""".format(
                                name=self.command.name(),
                                params=" ".join(params_syntax),
                                desc="\n".join(params_desc))
                            )

            field_count += 1

            if field_count % 2 == 1:
                embed.add_field(name="\u200B", value="\u200B", inline=True)

            if field_count % 2 == 0 and field_count < len(self.syntaxes):
                embed.add_field(name="\u200B", value="\u200B", inline=False)

        return embed
