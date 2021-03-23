from typing import List

from discord import Message

from application.database.db_memo import DbMemo
from application.param.app_params import ApplicationParams
from core.command.base import BaseCommand
from core.executor.executors import TextParamExecutor, FixedValueParamExecutor
from core.message.messages import Messages
from core.param.params import CommandParam, ParamType
from core.param.syntax import CommandSyntax
from core.utils.parsing_utils import ParsingUtils


class MemoCommand(BaseCommand):
    _MAX_PER_USER = 20

    @staticmethod
    def name() -> str:
        return "memo"

    @staticmethod
    def description() -> str:
        return "Enregistre des mémos pour les relire plus tard."

    @classmethod
    def description_details(cls) -> [str, None]:
        return "Tu peux enregistrer {} mémos.".format(cls._MAX_PER_USER)

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        name_param = CommandParam("nom", "Nom du mémo.", ParamType.TEXT)
        name_part_param = CommandParam("nom", "Une partie du nom du mémo.", ParamType.TEXT)
        edit_param = CommandParam("edit", "", ParamType.FIXED_VALUE)

        syntaxes = [
            CommandSyntax("Ajoute un mémo",
                          cls._add_memo,
                          name_param,
                          ApplicationParams.SENTENCE
                          ),
            CommandSyntax("Lis un mémo",
                          cls._get_memo,
                          name_part_param
                          ),
            CommandSyntax("Liste tes mémos",
                          cls._get_memo_list,
                          ApplicationParams.INFO
                          ),
            CommandSyntax("Édite un mémo",
                          cls._edit_memo,
                          name_param,
                          edit_param,
                          ApplicationParams.SENTENCE
                          ),
            CommandSyntax("Supprime un mémo",
                          cls._remove_memo,
                          name_param,
                          ApplicationParams.STOP
                          )
        ]

        return syntaxes

    @classmethod
    def _add_memo(cls, message: Message, name_executor: TextParamExecutor, content_executor: TextParamExecutor):
        memo_count = DbMemo.count_user_memos(message.author.id)

        if memo_count >= cls._MAX_PER_USER:
            cls._reply(message, ("Tu as déjà enregistré {} mémos, dis-donc tu ne crois pas "
                                 "qu'il serait temps de faire un peu de ménage ? :smirk:"
                                 ).format(cls._MAX_PER_USER)
                       )
            return

        name = name_executor.get_text().replace("`", "")

        if DbMemo.add_memo(message.author.id, name, ParsingUtils.format_links(content_executor.get_text())):
            cls._reply(message, "Mémo [**{}**] ajouté !".format(name))
        else:
            cls._display_error(message, "Le mémo [**{}**] existe déjà, veux-tu l'éditer ?".format(name))

    # noinspection PyUnusedLocal
    @classmethod
    def _edit_memo(cls, message: Message, name_executor: TextParamExecutor, edit_executor: FixedValueParamExecutor,
                   content_executor: TextParamExecutor):
        if DbMemo.edit_memo(message.author.id, name_executor.get_text(), content_executor.get_text()):
            cls._reply(message, "Mémo [**{}**] édité !".format(name_executor.get_text()))
        else:
            cls._display_error(message, "Aucun mémo trouvé avec le nom `{}`.".format(name_executor.get_text()))

    @classmethod
    def _get_memo(cls, message: Message, name_executor: TextParamExecutor):
        memo = DbMemo.get_memo(message.author.id, name_executor.get_text())
        if memo:
            cls._reply(message,
                       Messages.get_memo_embed(memo.name, memo.content),
                       20)
        else:
            cls._display_error(message, "Aucun mémo trouvé contenant le terme `{}`.".format(name_executor.get_text()))

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_memo(cls, message: Message, name_executor: TextParamExecutor, stop_executor: FixedValueParamExecutor):
        if DbMemo.remove_memo(message.author.id, name_executor.get_text()):
            cls._reply(message, "Mémo [**{}**] supprimé !".format(name_executor.get_text()))
        else:
            cls._display_error(message, "Aucun mémo trouvé avec le nom `{}`.".format(name_executor.get_text()))

    # noinspection PyUnusedLocal
    @classmethod
    def _get_memo_list(cls, message: Message, info_executor: FixedValueParamExecutor):
        memos = DbMemo.get_memo_list(message.author.id)

        if not memos:
            cls._reply(message, "Tu n'as aucun mémo enregistré.")
        else:
            cls._reply(message,
                       Messages.get_memo_embed("Mes mémos",
                                               "\u00A0\u00A0\u00A0".join(["`" + memo + "`" for memo in memos]),
                                               "{} / {}".format(len(memos), cls._MAX_PER_USER)
                                               ),
                       20
                       )
