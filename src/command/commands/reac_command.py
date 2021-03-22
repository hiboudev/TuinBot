from typing import List

from discord import Message

from command.command_base import BaseCommand
from command.params.application import ApplicationParams
from command.params.executors import UserParamExecutor, EmojiParamExecutor, FixedValueParamExecutor
from command.params.params import CommandParam, ParamType
from command.params.syntax import CommandSyntax
from command.types import HookType
from database.db_reaction import DbAutoReaction


class AutoReactionCommand(BaseCommand):

    @staticmethod
    def name() -> str:
        return "reac"

    @staticmethod
    def description() -> str:
        return "Ajoute une réaction automatique aux messages d'un tuin."

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        emoji_param = CommandParam("emoji", "Un emoji qui lui collera au cul pour un moment.", ParamType.EMOJI)

        syntaxes = [
            CommandSyntax("Ajoute une réaction sur un tuin",
                          cls._add_reaction,
                          ApplicationParams.USER,
                          emoji_param
                          ),
            CommandSyntax("Enlève ta réaction sur un tuin",
                          cls._remove_reaction,
                          ApplicationParams.USER,
                          ApplicationParams.STOP,
                          ),
            CommandSyntax("Liste les réactions mises sur un tuin",
                          cls._list_reactions,
                          ApplicationParams.USER,
                          ),
            CommandSyntax("Enlève toutes les réactions que les sales tuins t'ont mises",
                          cls._remove_all_reactions,
                          ApplicationParams.STOP,
                          )
        ]

        return syntaxes

    @classmethod
    def _add_reaction(cls, message: Message, user_executor: UserParamExecutor,
                      emoji_executor: EmojiParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoReaction.add_auto_reaction(message.guild.id,
                                                                         message.author.id,
                                                                         user_executor.get_user().id,
                                                                         emoji_executor.get_emoji()
                                                                         ),
                                        message):
            cls._reply(message,
                       "Réaction automatique %s ajoutée à **%s** !" % (
                           emoji_executor.get_emoji(), user_executor.get_user().display_name))

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_reaction(cls, message: Message, user_executor: UserParamExecutor,
                         stop_executor: FixedValueParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoReaction.remove_auto_reaction(message.guild.id,
                                                                            message.author.id,
                                                                            user_executor.get_user().id),
                                        message):
            cls._reply(message, "Réaction automatique retirée de **%s** !" % user_executor.get_user().display_name)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_all_reactions(cls, message: Message, stop_executor: FixedValueParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoReaction.remove_all_auto_reactions(message.guild.id,
                                                                                 message.author.id),
                                        message):
            cls._reply(message, "OK, j'ai viré les réactions automatiques que ces sales tuins t'avaient mises !")

    @classmethod
    def _list_reactions(cls, message: Message, user_executor: UserParamExecutor):
        reactions = DbAutoReaction.get_auto_reactions(message.guild.id,
                                                      user_executor.get_user().id)
        cls._reply(message,
                   "**%s** a %s réaction(s) automatique(s) : %s" % (
                       user_executor.get_user().display_name, len(reactions), " ".join(reactions)))

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.MESSAGE

    @classmethod
    def execute_message_hook(cls, message: Message):
        reactions = DbAutoReaction.get_auto_reactions(message.guild.id,
                                                      message.author.id)

        if reactions:
            cls._async(cls._execute_hook_async(message, reactions))

    @classmethod
    async def _execute_hook_async(cls, message: Message, reactions: List[str]):
        for reaction in reactions:
            await message.add_reaction(reaction)
