import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Callable

from discord import Message, Client, User

from database.database import Database
from utils.parsing_utils import ParsingUtils


class HookType(Enum):
    NONE = 1
    TYPING = 2
    MESSAGE = 3


class Command(ABC):

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @classmethod
    @abstractmethod
    def _execute(cls, message: Message, command_params: list, bot: Client):
        pass

    @classmethod
    @abstractmethod
    def get_help(cls) -> str:
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
    def execute(cls, message: Message, command_params: list, client: Client):
        if not command_params:
            cls._display_help(message)
        else:
            cls._execute(message, command_params, client)

    @classmethod
    def _display_error(cls, message: Message, error: str):
        cls._reply(message, "%s. Tapez **!%s** pour afficher l'aide." % (error, cls.name()))

    @classmethod
    def _display_help(cls, message: Message):
        cls._reply(message, cls.get_help(), cls._delete_delay_help())

    @classmethod
    def _execute_db_bool_request(cls, func: Callable, message):
        result = func()
        if not result:
            cls._reply(message, "Il n'y a rien à faire.")

        return result

    @staticmethod
    def _delete_delay() -> int:
        return 5

    @staticmethod
    def _delete_delay_help() -> int:
        return 20

    @classmethod
    def _reply(cls, message: Message, text: str, delete_delay: int = None):
        asyncio.create_task(cls._reply_and_delete(message, text, delete_delay))

    @classmethod
    async def _reply_and_delete(cls, message: Message, text: str, delay: int = None):
        response = await message.reply("%s" % text)
        await response.delete(delay=delay or cls._delete_delay())
        await message.delete(delay=delay or cls._delete_delay())


class TuinBotCommand(Command):

    @staticmethod
    def name() -> str:
        return "tuin"

    @classmethod
    def _execute(cls, message: Message, command_params: list, bot: Client):
        pass

    @classmethod
    def get_help(cls) -> str:
        help_mess = "Commandes disponibles :"

        for command in Commands.LIST:
            help_mess += "\n!%s" % command.name()
        help_mess += "\nTapez une commande pour voir sa page d'aide."

        return help_mess

    # TODO def description : pour l'aide générale et individuelle


class AutoReactionCommand(Command):

    @staticmethod
    def name() -> str:
        return "reac"

    @classmethod
    def _execute(cls, message: Message, command_params: list, client: Client):
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

    @classmethod
    def get_help(cls) -> str:
        return "!%s utilisateur emoji" % cls.name()

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


class Commands:
    LIST = [TuinBotCommand, AutoReactionCommand]
    _hooks: Dict = None

    # _hooks: Dict[HookType, Command] = None
    # cf. https://mypy.readthedocs.io/en/latest/generics.html#variance-of-generic-types
    # Command = TypeVar("Command", covariant=True)

    @classmethod
    def get_hooks(cls, hook_type: HookType) -> List[Command]:
        if cls._hooks is None:
            cls._hooks = {}
            for command in cls.LIST:
                if command.has_hook():
                    if command.hook_type() not in cls._hooks:
                        cls._hooks[command.hook_type()] = []
                    cls._hooks[command.hook_type()].append(command)

        return cls._hooks[hook_type]
