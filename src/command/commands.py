import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, TypeVar

from discord import Message, Client

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
            cls.display_help(message)
        else:
            cls._execute(message, command_params, client)

    @classmethod
    def display_error(cls, message: Message, error: str):
        asyncio.create_task(message.reply(
            "%s. Tapez **!%s** pour afficher l'aide." % (error, cls.name())
        ))

    @classmethod
    def display_help(cls, message: Message):
        asyncio.create_task(message.reply(cls.get_help()))

    @staticmethod
    def reply(message: Message, text: str):
        asyncio.create_task(message.reply(
            "%s" % text
        ))


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
        if num_parans < 1 or num_parans > 2:
            cls.display_error(message, "Nombre de paramètres incorrect")
            return

        """ TODO
        * utilisateur peut être une mention
        """

        # Param 1 : User or "stop" (to stop all others emoji on us)
        if command_params[0] == "stop":
            if Database().remove_all_auto_reactions(message.author.id):
                cls.reply(message, "OK, j'ai viré les réactions automatiques que ces sales tuins t'avaient mises !")
            else:
                cls.reply(message, "Il n'y a rien à faire.")
            return

        user = ParsingUtils.find_user(message.channel.members, command_params[0])
        if not user:
            cls.display_error(message, "Utilisateur introuvable")
            return

        # Param 2 missing
        if len(command_params) == 1:
            reactions = Database().get_auto_reactions(user.id)
            cls.reply(message, "%s a %s réaction(s) automatique(s) : %s" % (user.name, len(reactions), " ".join(reactions)))
            return

        # Param 2 : Emoji or "stop" (to stop our emoji on target user)
        if command_params[1] == "stop":
            if Database.remove_auto_reaction(message.author.id, user.id):
                cls.reply(message, "Réaction automatique retirée de %s !" % user.name)
            else:
                cls.reply(message, "Il n'y a rien à faire.")
        else:
            emoji_param = command_params[1]
            emoji = ParsingUtils.get_emoji(emoji_param, client)
            if not emoji:
                cls.display_error(message, "Emoji introuvable")
                return

            if Database.add_auto_reaction(message.author.id, user.id, emoji):
                cls.reply(message, "Réaction automatique %s ajoutée à %s !" % (emoji, user.name))
            else:
                cls.reply(message, "Il n'y a rien à faire.")

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
