from typing import List

from discord import Message, TextChannel, Member

from application.database.db_typing_mess import DbTypingMessage, TypingMessage
from application.message.messages import AppMessages
from application.param.app_params import ApplicationParams
from core.command.base import BaseCommand
from core.command.types import HookType
from core.executor.executors import TextParamExecutor, UserParamExecutor, FixedValueParamExecutor
from core.param.syntax import CommandSyntax
from core.utils.parsing_utils import ParsingUtils
from core.utils.sanitizer import Sanitizer


class TypingMessageCommand(BaseCommand):
    # TODO commande très semblable à reply, généraliser ?

    _MAX_PER_USER = 1

    @staticmethod
    def name() -> str:
        return "tape"

    @staticmethod
    def description() -> str:
        return "Affiche un message à un tuin la prochaine fois qu'il tapera sur son clavier."

    @classmethod
    def description_details(cls) -> [str, None]:
        return ("Le message n'apparaîtra que dans le salon où la commande a été tapée."
                " Tu peux laisser 1 message par tuin,"
                " et un tuin peut avoir au maximum {} message(s) planifié(s) sur lui."
                ).format(cls._MAX_PER_USER)

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        syntaxes = [
            CommandSyntax("Enregistre un message",
                          cls._add_typing_message,
                          ApplicationParams.USER,
                          ApplicationParams.RECORDED_MESSAGE
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
        typing_count = DbTypingMessage.count_typing_messages(message.guild.id, user_executor.get_user().id,
                                                             message.author.id)

        if typing_count >= cls._MAX_PER_USER:
            cls._reply(
                message,
                "Oups, il y a déjà {} message(s) enregistré(s) pour **{}**, il va falloir attendre ton tour !".format(
                    typing_count, Sanitizer.user_name(user_executor.get_user().display_name))
            )
            return

        content = ParsingUtils.format_links(ParsingUtils.to_single_line(text_executor.get_text()))

        if cls._execute_db_bool_request(lambda:
                                        DbTypingMessage.add_typing_message(message.guild.id,
                                                                           message.channel.id,
                                                                           message.author.id,
                                                                           user_executor.get_user().id,
                                                                           content
                                                                           ),
                                        message):
            cls._reply(message,
                       "Message enregistré pour **%s** !" % Sanitizer.user_name(user_executor.get_user().display_name))

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
                       "Message pour **%s** effacé !" % Sanitizer.user_name(user_executor.get_user().display_name))

    # noinspection PyUnusedLocal
    @classmethod
    def _show_typing_message(cls, message: Message, user_executor: UserParamExecutor):
        sentence = DbTypingMessage.get_typing_message_content(message.guild.id,
                                                              message.author.id,
                                                              user_executor.get_user().id)

        if not sentence:
            cls._reply(message, "Aucun message enregistré pour **{}** !".format(
                Sanitizer.user_name(user_executor.get_user().display_name)))
        else:
            cls._reply(message,
                       "Message enregistré pour **{}** : {}".format(
                           Sanitizer.user_name(user_executor.get_user().display_name),
                           sentence)
                       )

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.TYPING

    @classmethod
    def execute_typing_hook(cls, channel: TextChannel, user: Member):
        messages = DbTypingMessage.use_typing_messages(user.guild.id, channel.id, user.id)

        if messages:
            cls._async(cls._execute_hook_async(channel, user, messages))

    @classmethod
    async def _execute_hook_async(cls, channel: TextChannel, user: Member, messages: List[TypingMessage]):
        for message in messages:
            author = channel.guild.get_member(message.author_id)

            embed = AppMessages.get_recorded_message_embed(
                message.message,
                user.id,
                None if not author else author.display_name
            )

            await channel.send(embed=embed)
