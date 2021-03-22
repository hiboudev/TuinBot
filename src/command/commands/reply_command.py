from typing import List

from discord import Message, TextChannel, Member

from command.command_base import BaseCommand
from command.messages import Messages
from command.params.application import ApplicationParams
from command.params.executors import TextParamExecutor, UserParamExecutor, FixedValueParamExecutor
from command.params.params import CommandParam, ParamType
from command.params.syntax import CommandSyntax
from command.types import HookType
from database.db_reply import DbAutoReply


class ReplyMessageCommand(BaseCommand):
    _MAX_PER_USER = 3

    @staticmethod
    def name() -> str:
        return "rep"

    @staticmethod
    def description() -> str:
        return "Affiche une réponse au prochain message d'un tuin."

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        syntaxes = [
            CommandSyntax("Enregistre un message",
                          cls._add_reply,
                          ApplicationParams.USER,
                          CommandParam("texte", "Le texte, entre guillemets.", ParamType.TEXT)
                          ),
            CommandSyntax("Retire ton message",
                          cls._remove_reply,
                          ApplicationParams.USER,
                          ApplicationParams.STOP
                          ),
            CommandSyntax("Vérifie ton message",
                          cls._show_reply,
                          ApplicationParams.USER
                          ),
        ]

        return syntaxes

    # noinspection PyUnusedLocal
    @classmethod
    def _add_reply(cls, message: Message, user_executor: UserParamExecutor, text_executor: TextParamExecutor):
        typing_count = DbAutoReply.count_auto_replys(message.guild.id, user_executor.get_user().id, message.author.id)

        if typing_count >= cls._MAX_PER_USER:
            cls._reply(
                message,
                "Oups, il y a déjà {} messages enregistrés pour **{}**, il va falloir attendre ton tour !".format(
                    typing_count, user_executor.get_user().display_name)
            )

        elif cls._execute_db_bool_request(lambda:
                                          DbAutoReply.add_auto_reply(message.guild.id,
                                                                     message.author.id,
                                                                     user_executor.get_user().id,
                                                                     text_executor.get_text()
                                                                     ),
                                          message):
            cls._reply(message,
                       "Message enregistré pour **%s** !" % user_executor.get_user().display_name)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_reply(cls, message: Message, user_executor: UserParamExecutor,
                      stop_executor: FixedValueParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoReply.remove_auto_reply(message.guild.id,
                                                                      message.author.id,
                                                                      user_executor.get_user().id
                                                                      ),
                                        message):
            cls._reply(message,
                       "Message pour **%s** effacé !" % user_executor.get_user().display_name)

    # noinspection PyUnusedLocal
    @classmethod
    def _show_reply(cls, message: Message, user_executor: UserParamExecutor):
        sentence = DbAutoReply.get_auto_reply_content(message.guild.id,
                                                      message.author.id,
                                                      user_executor.get_user().id)

        if not sentence:
            cls._reply(message, "Aucun message enregistré pour **{}** !".format(user_executor.get_user().display_name))
        else:
            cls._reply(message,
                       "Message enregistré pour **{}** : *{}*".format(user_executor.get_user().display_name,
                                                                      sentence.replace("*", "\\*"))
                       )

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.MESSAGE

    @classmethod
    def execute_hook(cls, message: Message = None, typing_channel: TextChannel = None, typing_user: Member = None):
        messages = DbAutoReply.use_auto_replys(message.guild.id, message.author.id)

        if messages:
            for text_message in messages:
                author = message.guild.get_member(text_message.author_id)

                embed = Messages.get_hook_embed(
                    description="{} <@{}>".format(text_message.message, message.author.id)
                )

                if author:
                    embed.set_footer(text="Signé {}".format(author.display_name))

                cls._reply(message, embed)
