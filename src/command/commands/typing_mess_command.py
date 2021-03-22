from typing import List

from discord import Message, TextChannel, Member

from command.command_base import BaseCommand
from command.messages import Messages
from command.params.application import ApplicationParams
from command.params.executors import TextParamExecutor, UserParamExecutor, FixedValueParamExecutor
from command.params.params import CommandParam, ParamType
from command.params.syntax import CommandSyntax
from command.types import HookType
from database.db_typing_mess import DbTypingMessage, TypingMessage


class TypingMessageCommand(BaseCommand):
    _MAX_PER_USER = 3

    @staticmethod
    def name() -> str:
        return "tape"

    @staticmethod
    def description() -> str:
        return "Affiche un message à un tuin la prochaine fois qu'il tapera sur son clavier."

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        syntaxes = [
            CommandSyntax("Enregistre un message",
                          cls._add_typing_message,
                          ApplicationParams.USER,
                          CommandParam("texte", "Le texte, entre guillemets.", ParamType.TEXT)
                          ),
            CommandSyntax("Retire ton message",
                          cls._remove_typing_message,
                          ApplicationParams.USER,
                          ApplicationParams.STOP
                          ),
            CommandSyntax("Vérifie ton message",
                          cls._show_typing_message,
                          ApplicationParams.USER
                          ),
        ]

        return syntaxes

    # noinspection PyUnusedLocal
    @classmethod
    def _add_typing_message(cls, message: Message, user_executor: UserParamExecutor, text_executor: TextParamExecutor):
        typing_count = DbTypingMessage.count_typing_messages(message.guild.id, user_executor.get_user().id)

        if typing_count >= cls._MAX_PER_USER:
            cls._reply(
                message,
                "Oups, il y a déjà {} messages enregistrés pour **{}**, il va falloir attendre ton tour !".format(
                    typing_count, user_executor.get_user().display_name)
            )

        elif cls._execute_db_bool_request(lambda:
                                          DbTypingMessage.add_typing_message(message.guild.id,
                                                                             message.author.id,
                                                                             user_executor.get_user().id,
                                                                             text_executor.get_text()
                                                                             ),
                                          message):
            cls._reply(message,
                       "Message enregistré pour **%s** !" % user_executor.get_user().display_name)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_typing_message(cls, message: Message, user_executor: UserParamExecutor,
                               stop_executor: FixedValueParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbTypingMessage.remove_typing_message(message.guild.id,
                                                                              message.author.id,
                                                                              user_executor.get_user().id
                                                                              ),
                                        message):
            cls._reply(message,
                       "Message pour **%s** effacé !" % user_executor.get_user().display_name)

    # noinspection PyUnusedLocal
    @classmethod
    def _show_typing_message(cls, message: Message, user_executor: UserParamExecutor):
        sentence = DbTypingMessage.get_typing_message_content(message.guild.id,
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
        return HookType.TYPING

    @classmethod
    def execute_hook(cls, message: Message = None, typing_channel: TextChannel = None, typing_user: Member = None):
        messages = DbTypingMessage.use_typing_messages(typing_user.guild.id, typing_user.id)

        if messages:
            cls._async(cls._execute_hook_async(typing_channel, typing_user, messages))

    @classmethod
    async def _execute_hook_async(cls, channel: TextChannel, user: Member, messages: List[TypingMessage]):
        for message in messages:
            author = channel.guild.get_member(message.author_id)

            embed = Messages.get_hook_embed(
                description="{} <@{}>".format(message.message, user.id)
            )

            if author:
                embed.set_footer(text="Signé {}".format(author.display_name))

            await channel.send(embed=embed)
