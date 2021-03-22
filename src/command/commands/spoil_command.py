from typing import List

from discord import Message, TextChannel, User, Embed, Member

from command.command_base import BaseCommand
from command.params.application import ApplicationParams
from command.params.executors import UserParamExecutor, FixedValueParamExecutor
from command.params.params import CommandParam, ParamType
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
            CommandSyntax("Regarde quel tuin a mis un spoiler sur un tuin",
                          cls._display_spoiler_info,
                          ApplicationParams.USER,
                          ApplicationParams.INFO
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
    def execute_hook(cls, message: Message = None, typing_channel: TextChannel = None, typing_user: Member = None):
        if not cls._can_execute_hook(message):
            return

        spoil_author_id = DbAutoSpoiler.use_auto_spoiler(message.guild.id,
                                                         message.author.id)

        if spoil_author_id:
            cls._async(cls._execute_hook_async(message, spoil_author_id))

    @staticmethod
    def _can_execute_hook(message: Message) -> bool:
        # Don't apply this hook on another bot command.
        if message.content.startswith("!"):
            return False

        # With Embed the link disapears, we need to add a field but it's too big.
        # So we bypass hook.
        if "http" in message.content:
            return False

        # Attachements other than images are not well managed in embeds, so don't process.
        if message.attachments and not message.attachments[0].width:
            return False

        return True

    @staticmethod
    async def _execute_hook_async(message: Message, author_id: int):
        content = message.content

        embed = Embed(
            title=":popcorn:\u00A0\u00A0\u00A0\u00A0Avis à la population !\u00A0\u00A0\u00A0\u00A0:popcorn:",
            description="Le tuin **{}** a une déclaration à faire ! :partying_face:\n\n{}".format(
                message.author.display_name,
                ":point_right: \u00A0\u00A0\u00A0\u00A0||\u00A0\u00A0*"
                + content + "*\u00A0\u00A0||" if content else ""
            ))

        author = message.guild.get_member(author_id)
        if author:
            embed.set_footer(text="Spoiler trollé par le tuin {}".format(author.display_name))

        # If an image is uploaded with message, adds it to embed.
        if message.attachments and message.attachments[0].width:
            embed.set_image(url=message.attachments[0].proxy_url)

        await message.channel.send(embed=embed)
        await message.delete()

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
                        stop_executor: FixedValueParamExecutor):
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
                              info_executor: FixedValueParamExecutor):
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
