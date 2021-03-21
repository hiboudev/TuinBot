from typing import List

from discord import Message, TextChannel, User

from command.command_base import BaseCommand
from command.params.application import ApplicationParams
from command.params.executors import UserParamExecutor, SingleValueParamExecutor
from command.params.params import CommandParam, ParamType, SingleValueParamConfig
from command.params.syntax import CommandSyntax
from command.types import HookType
from database.db_spoiler import DbAutoSpoiler


class AutoSpoilerCommand(BaseCommand):

    @staticmethod
    def name() -> str:
        return "spoil"

    @staticmethod
    def description() -> str:
        return "Ajoute un spoiler sur le prochain message d'un tuin."

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        info_param = CommandParam("info", "", ParamType.SINGLE_VALUE, SingleValueParamConfig("info"))

        syntaxes = [
            CommandSyntax("Ajoute un spoiler sur un tuin",
                          cls._add_spoiler,
                          ApplicationParams.USER
                          ),
            CommandSyntax("Retire ton spoiler sur un tuin",
                          cls._remove_spoiler,
                          ApplicationParams.USER,
                          ApplicationParams.STOP
                          ),
            CommandSyntax("Affiche les infos de spoiler d'un tuin",
                          cls._display_spoiler_info,
                          ApplicationParams.USER,
                          info_param
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
        # TODO voir à ne rien faire si le message contient un embed
        if message.content.startswith("!"):
            return

        if DbAutoSpoiler.use_auto_spoiler(message.guild.id,
                                          message.author.id):
            cls._async(cls._execute_hook_async(message))

    @staticmethod
    async def _execute_hook_async(message: Message):
        if not isinstance(message.channel, TextChannel):
            return

        attachment = None
        if message.attachments:
            attachment = await message.attachments[0].to_file(use_cached=True, spoiler=True)

        content = message.content
        if message.content and "http" not in message.content:
            content = "*" + message.content + "*"

        await message.channel.send(
            content=":popcorn: Avis à la population ! **{}** va faire une déclaration ! :popcorn:\n\n{}".format(
                message.author.display_name,
                ":point_right: \t||\u00A0" + content + "\u00A0||" if content else ""
            ),
            # embed=None if not message.embeds else message.embeds[0],
            file=attachment
        )
        await message.delete()

    # noinspection PyUnusedLocal
    @classmethod
    def _add_spoiler(cls, message: Message, user_executor: UserParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoSpoiler.add_auto_spoiler(message.guild.id,
                                                                       message.author.id,
                                                                       user_executor.get_user().id
                                                                       ),
                                        message):
            cls._reply(message,
                       "Spoiler ajouté au prochain message de **{}** !".format(user_executor.get_user().display_name))

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_spoiler(cls, message: Message, user_executor: UserParamExecutor,
                        stop_executor: SingleValueParamExecutor):
        if cls._execute_db_bool_request(lambda:
                                        DbAutoSpoiler.remove_auto_spoiler(message.guild.id,
                                                                          message.author.id,
                                                                          user_executor.get_user().id
                                                                          ),
                                        message):
            cls._reply(message, "Spoiler retiré de **{}** !".format(user_executor.get_user().display_name))

    # noinspection PyUnusedLocal
    @classmethod
    def _display_spoiler_info(cls, message: Message, user_executor: UserParamExecutor,
                              info_executor: SingleValueParamExecutor):
        author_id = DbAutoSpoiler.get_auto_spoiler_author(message.guild.id, user_executor.get_user().id)

        if author_id is None:
            cls._reply(message, "Aucun spoiler sur **{}** !".format(user_executor.get_user().display_name))
        else:
            user: User = message.guild.get_member(author_id)

            if not user:
                cls._reply(message, "Oups ! Il semble qu'il y ait eu un soucis pour retrouver le tuin !")
            else:
                cls._reply(message,
                           "**{}** a mis un spoiler sur **{}** !".format(user.display_name,
                                                                         user_executor.get_user().display_name))
