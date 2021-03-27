from typing import List

from discord import Message

from application.database.db_memo import DbMemo
from application.message.messages import AppMessages
from application.param.app_params import ApplicationParams
from core.command.base import BaseCommand
from core.executor.executors import TextParamExecutor, FixedValueParamExecutor, IntParamExecutor
from core.param.params import CommandParam, ParamType, TextMinMaxParamConfig, NumberMinMaxParamConfig
from core.param.syntax import CommandSyntax
from core.utils.parsing_utils import ParsingUtils


class MemoCommand(BaseCommand):
    _MAX_PER_USER = 20
    _MAX_LINES = 10
    _MAX_CHARS = 1000

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
        # Limit to 3 chars only when creating memo.
        name_param_creation = CommandParam("nom", "Nom du mémo", ParamType.TEXT, TextMinMaxParamConfig(3))
        name_param_use = CommandParam("nom", "Nom exact du mémo", ParamType.TEXT)
        name_part_param = CommandParam("nom", "Une partie du nom du mémo", ParamType.TEXT)
        delete_param = CommandParam("suppr", "", ParamType.FIXED_VALUE)

        syntaxes = [
            CommandSyntax("Ajoute un mémo",
                          cls._add_memo,
                          name_param_creation,
                          CommandParam(ApplicationParams.SENTENCE.name,
                                       ApplicationParams.SENTENCE.description,
                                       ParamType.TEXT,
                                       TextMinMaxParamConfig(max_length=cls._MAX_CHARS))
                          ),
            CommandSyntax("Lis un mémo",
                          cls._get_memo,
                          name_part_param
                          ),
            CommandSyntax("Liste tes mémos",
                          cls._get_memo_list,
                          ApplicationParams.LIST
                          ),
            CommandSyntax("Ajoute une ligne à un mémo",
                          cls._edit_memo,
                          name_part_param,
                          CommandParam("ajout", "", ParamType.FIXED_VALUE),
                          ApplicationParams.SENTENCE
                          ),
            CommandSyntax("Lis une ligne d'un mémo",  # TODO indiquer que le message restera
                          cls._get_memo_line,
                          name_part_param,
                          CommandParam("ligne", "", ParamType.FIXED_VALUE),
                          CommandParam("numéro", "Numéro de la ligne", ParamType.INT,
                                       NumberMinMaxParamConfig(1, cls._MAX_LINES))
                          ),
            CommandSyntax("Supprime une ligne d'un mémo",
                          cls._remove_memo_line,
                          name_param_use,
                          CommandParam("ligne", "", ParamType.FIXED_VALUE),
                          CommandParam("numéro", "Numéro de la ligne", ParamType.INT,
                                       NumberMinMaxParamConfig(1, cls._MAX_LINES)),
                          delete_param
                          ),
            CommandSyntax("Supprime un mémo",
                          cls._remove_memo,
                          name_param_use,
                          delete_param
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

        name = ParsingUtils.to_single_line(name_executor.get_text().replace("`", ""))
        content = ParsingUtils.to_single_line(content_executor.get_text())

        if DbMemo.add_memo(message.author.id, name, content):
            cls._reply(message, "Mémo [**{}**] ajouté !".format(name))
        else:
            cls._display_error(message, "Le mémo [**{}**] existe déjà, veux-tu l'éditer ?".format(name))

    @classmethod
    def _get_memo(cls, message: Message, name_executor: TextParamExecutor):
        memo = DbMemo.get_memo(message.author.id, name_executor.get_text())

        if not memo:
            cls._display_error(message, "Aucun mémo trouvé avec le terme `{}`.".format(
                name_executor.get_text()))
            return

        content = "\n".join([f"`{line_count + 1}`\u00A0\u00A0\u00A0{line}"
                             for line_count, line in enumerate(memo.lines)
                             ])

        cls._reply(message, AppMessages.get_memo_embed(memo.name, content), 20)

    # noinspection PyUnusedLocal
    @classmethod
    def _edit_memo(cls, message: Message, name_executor: TextParamExecutor, edit_executor: FixedValueParamExecutor,
                   content_executor: TextParamExecutor):

        memo = DbMemo.get_memo(message.author.id, name_executor.get_text())
        if not memo:
            cls._display_error(message, "Aucun mémo trouvé avec le nom `{}`.".format(name_executor.get_text()))
            return

        line_count = len(memo.lines)
        if line_count >= cls._MAX_LINES:
            cls._display_error(message, "Le mémo [**{}**] fait déjà {} lignes, tu ne peux plus rien rajouter.".format(
                name_executor.get_text(), cls._MAX_LINES))
            return

        total_char_count = len("".join(memo.lines)) + len(content_executor.get_text())
        if total_char_count > cls._MAX_CHARS:
            cls._display_error(message,
                               "Le mémo [**{}**] va dépasser les {} caractères, il faut en créer un autre.".format(
                                   name_executor.get_text(), cls._MAX_CHARS))
            return

        if cls._execute_db_bool_request(lambda: DbMemo.edit_memo(message.author.id,
                                                                 name_executor.get_text(),
                                                                 content_executor.get_text()),
                                        message):
            cls._reply(message, "Mémo [**{}**] édité !".format(memo.name))

    # noinspection PyUnusedLocal
    @classmethod
    def _get_memo_line(cls, message: Message, name_executor: TextParamExecutor, line_executor: FixedValueParamExecutor,
                       int_executor: IntParamExecutor):
        # Just to display a better error message
        line_count = DbMemo.count_memo_lines(message.author.id, name_executor.get_text())
        if line_count == 0:
            cls._display_error(message, "Aucun mémo trouvé avec le terme `{}`.".format(name_executor.get_text()))
            return

        if line_count < int_executor.get_int():
            # TODO on veut afficher le nom complet du mémo, par le morceau tapé par le user
            cls._display_error(message,
                               "Le mémo [**{}**] n'a que `{}` ligne(s).".format(name_executor.get_text(),
                                                                                line_count))
            return

        memo_line = DbMemo.get_memo_line(message.author.id, name_executor.get_text(), int_executor.get_int())

        if not memo_line:
            cls._display_error(message, "Je n'ai rien trouvé.")
            return

        cls._reply(message, AppMessages.get_memo_line_embed(memo_line), -1)

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_memo_line(cls, message: Message, name_executor: TextParamExecutor,
                          line_executor: FixedValueParamExecutor,
                          int_executor: IntParamExecutor, delete_executor: FixedValueParamExecutor):
        # Just to display a better error message
        line_count = DbMemo.count_memo_lines(message.author.id, name_executor.get_text(), True)
        if line_count == 0:
            cls._display_error(message, "Aucun mémo trouvé avec le nom `{}`.".format(name_executor.get_text()))
            return

        if line_count < int_executor.get_int():
            cls._display_error(message,
                               "Le mémo [**{}**] n'a que `{}` ligne(s).".format(name_executor.get_text(),
                                                                                line_count))
            return

        if cls._execute_db_bool_request(
                lambda: DbMemo.remove_memo_line(message.author.id, name_executor.get_text(), int_executor.get_int()),
                message):
            cls._reply(message,
                       f"Ligne `{int_executor.get_int()}` supprimée du mémo [**{name_executor.get_text()}**] !")

    # noinspection PyUnusedLocal
    @classmethod
    def _remove_memo(cls, message: Message, name_executor: TextParamExecutor, delete_executor: FixedValueParamExecutor):
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
            memo_list_str = []
            for memo in memos:
                memo_list_str.append("`{}`".format(memo.name.replace(" ", "\u00A0")))

            cls._reply(message,
                       AppMessages.get_memo_embed("Mes mémos",
                                                  "\u00A0\u0020\u00A0".join(memo_list_str),
                                                  "{} / {}".format(len(memos), cls._MAX_PER_USER)
                                                  ),
                       20
                       )
        # \u00A0\u0020\u00A0 : 2 unbreakable spaces to keep margin, and 1 normal space to wrap line between 2 titles
