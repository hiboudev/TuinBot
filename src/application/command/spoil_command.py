from typing import List

from discord import Message, User

from application.database.db_spoiler import DbAutoSpoiler
from application.message.messages import AppMessages
from application.param.app_params import ApplicationParams
from core.command.base import BaseCommand
from core.command.types import HookType
from core.executor.executors import UserParamExecutor, FixedValueParamExecutor
from core.param.syntax import CommandSyntax
from core.utils.parsing_utils import ParsingUtils


class AutoSpoilerCommand(BaseCommand):

    @staticmethod
    def name() -> str:
        return "spoil"

    @staticmethod
    def description() -> str:
        return "Ajoute un spoiler sur le prochain message d'un tuin."

    @classmethod
    def description_details(cls) -> [str, None]:
        return ("Le spoiler s'activera uniquement dans le salon où la commande a été tapée."
                " Un tuin peut avoir au maximum 1 spoiler planifié sur lui."
                )

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
            CommandSyntax("Regarde quel tuin a mis un spoiler sur un autre tuin",
                          cls._display_spoiler_info,
                          ApplicationParams.USER,
                          ApplicationParams.INFO
                          )
        ]

        return syntaxes

    @classmethod
    def _add_spoiler(cls, message: Message, user_executor: UserParamExecutor):
        if DbAutoSpoiler.add_auto_spoiler(message.guild.id,
                                          message.channel.id,
                                          message.author.id,
                                          user_executor.get_user().id
                                          ):
            cls._reply(message,
                       "Spoiler ajouté au prochain message de **{}** !".format(user_executor.get_user().display_name))
        else:
            cls._reply(message,
                       "Un spoiler est déjà mis sur **{}**.".format(user_executor.get_user().display_name))

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

    @staticmethod
    def has_hook() -> bool:
        return True

    @staticmethod
    def hook_can_delete_message() -> bool:
        return True

    @staticmethod
    def hook_type() -> HookType:
        return HookType.MESSAGE

    @classmethod
    def execute_message_hook(cls, message: Message) -> bool:
        if not cls._can_execute_hook(message):
            return False

        spoil_author_id = DbAutoSpoiler.use_auto_spoiler(message.guild.id,
                                                         message.channel.id,
                                                         message.author.id)

        if spoil_author_id:
            cls._async(cls._execute_hook_async(message, spoil_author_id))
            return True

        return False

    @staticmethod
    def _can_execute_hook(message: Message) -> bool:
        # Don't apply this hook on another bot command.
        if message.content.startswith("!"):
            return False

        # Don't apply if message is only a link
        if ParsingUtils.is_unique_link(message.content):
            return False

        # Attachements other than images are not well managed in embeds, so don't process.
        if message.attachments and not message.attachments[0].width:
            return False

        return True

    @staticmethod
    async def _execute_hook_async(message: Message, author_id: int):
        extracts = ParsingUtils.extract_links(message.content)

        user_message = "**" + extracts.message + "**" if extracts.message else ""
        description = ("Le tuin **{username}** a une déclaration à faire ! :partying_face:\n\n"
                       ":point_right: \u00A0\u00A0\u00A0\u00A0"
                       "||\u00A0\u00A0{user_message}\u00A0\u00A0{message_links_sep}{links}||"
                       ).format(username=message.author.display_name,
                                user_message=user_message,
                                message_links_sep="\n" if extracts.message and extracts.links else "",
                                links="\n".join(extracts.links)
                                )

        embed = AppMessages.get_hook_embed(
            title=":popcorn:\u00A0\u00A0\u00A0\u00A0Avis à la population !\u00A0\u00A0\u00A0\u00A0:popcorn:",
            description=description
        )

        author = message.guild.get_member(author_id)
        if author:
            embed.set_footer(text="Spoiler trollé par le tuin {}".format(author.display_name))

        # If an image is uploaded with message, adds it to embed.
        if message.attachments and message.attachments[0].width:
            embed.set_image(url=message.attachments[0].proxy_url)

        await message.channel.send(embed=embed)
        await message.delete()
