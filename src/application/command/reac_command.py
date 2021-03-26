from typing import List

from discord import Message

from application.database.db_reaction import DbAutoReaction
from application.param.app_params import ApplicationParams
from core.command.base import BaseCommand
from core.command.types import HookType
from core.executor.executors import UserParamExecutor, EmojiParamExecutor, FixedValueParamExecutor
from core.param.params import CommandParam, ParamType
from core.param.syntax import CommandSyntax


class AutoReactionCommand(BaseCommand):
    _MAX_REACTION_PER_TARGET = 6

    @staticmethod
    def name() -> str:
        return "reac"

    @staticmethod
    def description() -> str:
        return "Ajoute une réaction automatique sous les messages d'un tuin."

    @classmethod
    def description_details(cls) -> [str, None]:
        return ("La réaction n'apparaîtra que dans le salon où la commande a été tapée."
                " Tu peux mettre 1 réaction par tuin,"
                " et un tuin peut avoir au maximum {} réactions sur lui."
                ).format(cls._MAX_REACTION_PER_TARGET)

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        emoji_param = CommandParam("emoji", "Un emoji qui lui collera au cul pour un moment", ParamType.EMOJI)

        syntaxes = [
            CommandSyntax("Ajoute une réaction",
                          cls._add_reaction,
                          ApplicationParams.USER,
                          emoji_param
                          ),
            CommandSyntax("Enlève ta réaction",
                          cls._remove_reaction,
                          ApplicationParams.USER,
                          ApplicationParams.STOP,
                          ),
            CommandSyntax("Affiche les réactions mises sur un tuin",
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

        # Check max emoji limit
        reaction_count = DbAutoReaction.count_total_target_reactions(message.guild.id,
                                                                     user_executor.get_user().id,
                                                                     message.author.id)
        if reaction_count >= cls._MAX_REACTION_PER_TARGET:
            cls._reply(message,
                       "Le tuin **{}** a déjà {} réactions sur lui, laissons-le respirer un peu.".format(
                           user_executor.get_user().display_name, reaction_count)
                       )
            return

        # Can add only one type of emoji per target, cause bot can't add the same several times.
        if DbAutoReaction.reaction_exists(message.guild.id,
                                          message.channel.id,
                                          user_executor.get_user().id,
                                          emoji_executor.get_emoji()):
            cls._reply(message,
                       "Cet emoji est déjà mis sur **%s** dans ce salon, il faudrait en choisir un autre." % (
                           user_executor.get_user().display_name))
            return

        if cls._execute_db_bool_request(lambda:
                                        DbAutoReaction.add_auto_reaction(message.guild.id,
                                                                         message.channel.id,
                                                                         message.author.id,
                                                                         user_executor.get_user().id,
                                                                         emoji_executor.get_emoji()
                                                                         ),
                                        message):
            cls._reply(message,
                       "Réaction %s ajoutée à **%s** !" % (
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
            cls._reply(message, "Réaction retirée de **%s** !" % user_executor.get_user().display_name)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_all_reactions(cls, message: Message, stop_executor: FixedValueParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoReaction.remove_all_auto_reactions(message.guild.id,
                                                                                 message.author.id),
                                        message):
            cls._reply(message, "OK, j'ai viré les réactions que ces sales tuins t'avaient mises !")

    @classmethod
    def _list_reactions(cls, message: Message, user_executor: UserParamExecutor):
        total_reactions = DbAutoReaction.get_auto_reactions(message.guild.id,
                                                            user_executor.get_user().id)

        channel_reaction_part = ""
        if total_reactions:
            channel_reaction_count = DbAutoReaction.count_channel_target_reactions(message.guild.id,
                                                                                   message.channel.id,
                                                                                   user_executor.get_user().id)
            channel_reaction_part = f" ({channel_reaction_count} dans ce salon)"

        reactions_part = " : %s" % " ".join(total_reactions) if total_reactions else ""

        cls._reply(message,
                   "**%s** a %s réaction(s)%s%s" % (user_executor.get_user().display_name,
                                                    len(total_reactions),
                                                    channel_reaction_part,
                                                    reactions_part
                                                    )
                   )

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.MESSAGE

    @classmethod
    def execute_message_hook(cls, message: Message) -> bool:
        reactions = DbAutoReaction.get_auto_reactions(message.guild.id,
                                                      message.author.id,
                                                      message.channel.id)

        if reactions:
            cls._async(cls._execute_hook_async(message, reactions))

        return False

    @classmethod
    async def _execute_hook_async(cls, message: Message, reactions: List[str]):
        # Note: when message is spoiled, addind reaction triggers an error cause message is deleted
        for reaction in reactions:
            await message.add_reaction(reaction)
