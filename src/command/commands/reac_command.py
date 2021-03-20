import asyncio
from typing import List

from discord import Message

from command.command_base import BaseCommand
from command.params.params import CommandParam, ParamType, \
    UserParamExecutor, EmojiParamExecutor, SingleValueParamConfig
from command.params.syntax import CommandSyntax
from command.types import HookType
from database.database import Database


class AutoReactionCommand(BaseCommand):

    @staticmethod
    def name() -> str:
        return "reac"

    @staticmethod
    def description() -> str:
        return "Ajoute une réaction automatique aux messages d'un tuin."

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        user_param = CommandParam("tuin", "Le nom ou une partie du nom du tuin.", ParamType.USER)
        emoji_param = CommandParam("emoji", "Un emoji qui lui collera au cul pour un moment.", ParamType.EMOJI)
        stop_param = CommandParam("stop", "", ParamType.SINGLE_VALUE, SingleValueParamConfig("stop"))

        syntaxes = [
            CommandSyntax("Ajoute une réaction sur un tuin",
                          cls._add_reaction,
                          user_param,
                          emoji_param
                          ),
            CommandSyntax("Enlève ta réaction sur un tuin",
                          cls._remove_reaction,
                          user_param,
                          stop_param
                          ),
            CommandSyntax("Liste les réactions mises sur un tuin",
                          cls._list_reactions,
                          user_param
                          ),
            CommandSyntax("Enlève toutes les réactions que les sales tuins t'ont mis",
                          cls._remove_all_reactions,
                          stop_param
                          )
        ]

        return syntaxes

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.MESSAGE

    @classmethod
    def execute_hook(cls, message: Message):
        reactions = Database().get_auto_reactions(message.guild.id,
                                                  message.author.id)

        for reaction in reactions:
            asyncio.create_task(message.add_reaction(reaction))

    @classmethod
    def _add_reaction(cls, message: Message, user_executor: UserParamExecutor, emoji_executor: EmojiParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        Database.add_auto_reaction(message.guild.id,
                                                                   message.author.id,
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
                                        Database.remove_auto_reaction(message.guild.id,
                                                                      message.author.id,
                                                                      user_executor.get_user().id),
                                        message):
            cls._reply(message, "Réaction automatique retirée de %s !" % user_executor.get_user().name)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_all_reactions(cls, message: Message, user_executor: UserParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        Database().remove_all_auto_reactions(message.guild.id,
                                                                             message.author.id),
                                        message):
            cls._reply(message, "OK, j'ai viré les réactions automatiques que ces sales tuins t'avaient mises !")

    @classmethod
    def _list_reactions(cls, message: Message, user_executor: UserParamExecutor):
        reactions = Database().get_auto_reactions(message.guild.id,
                                                  user_executor.get_user().id)
        cls._reply(message,
                   "%s a %s réaction(s) automatique(s) : %s" % (
                       user_executor.get_user().name, len(reactions), " ".join(reactions)))
