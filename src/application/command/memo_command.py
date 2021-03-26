import re
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
        name_param_use = CommandParam("nom", "Nom du mémo", ParamType.TEXT)
        name_part_param = CommandParam("nom", "Une partie du nom du mémo", ParamType.TEXT)

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
            # CommandSyntax("Lis un mémo via son numéro",
            #               cls._get_memo_by_position,
            #               CommandParam("numéro", "Le numéro du mémo affiché dans la liste", ParamType.INT,
            #                            NumberMinMaxParamConfig(1, cls._MAX_PER_USER))
            #               ),
            CommandSyntax("Ajoute une ligne à un mémo",
                          cls._edit_memo,
                          name_param_use,
                          CommandParam("edit", "", ParamType.FIXED_VALUE),
                          ApplicationParams.SENTENCE
                          ),
            CommandSyntax("Lis une ligne d'un mémo",
                          cls._get_memo_line,
                          name_part_param,
                          CommandParam("ligne", "", ParamType.FIXED_VALUE),
                          CommandParam("numéro", "Numéro de la ligne", ParamType.INT,
                                       NumberMinMaxParamConfig(1, cls._MAX_LINES))
                          ),
            CommandSyntax("Supprime un mémo",
                          cls._remove_memo,
                          name_param_use,
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

        name = ParsingUtils.to_single_line(name_executor.get_text().replace("`", ""))
        content = "`1`\u00A0\u00A0\u00A0" + ParsingUtils.to_single_line(content_executor.get_text())

        if DbMemo.add_memo(message.author.id, name, content):
            cls._reply(message, "Mémo [**{}**] ajouté !".format(name))
        else:
            cls._display_error(message, "Le mémo [**{}**] existe déjà, veux-tu l'éditer ?".format(name))

    # noinspection PyUnusedLocal
    @classmethod
    def _edit_memo(cls, message: Message, name_executor: TextParamExecutor, edit_executor: FixedValueParamExecutor,
                   content_executor: TextParamExecutor):

        memo = DbMemo.get_memo(message.author.id, name_executor.get_text())
        if not memo:
            cls._display_error(message, "Aucun mémo trouvé avec le nom `{}`.".format(name_executor.get_text()))
            return

        line_count = ParsingUtils.count_lines(memo.content)
        if line_count >= cls._MAX_LINES:
            cls._display_error(message, "Le mémo [**{}**] fait déjà {} lignes, tu ne peux plus rien rajouter.".format(
                name_executor.get_text(), cls._MAX_LINES))
            return

        add_content = f"\n`{line_count + 1}`\u00A0\u00A0\u00A0" + content_executor.get_text()

        total_char_count = len(memo.content) + len(add_content)
        if total_char_count > cls._MAX_CHARS:
            cls._display_error(message,
                               "Le mémo [**{}**] va dépasser les {} caractères, il faut en créer un autre.".format(
                                   name_executor.get_text(), cls._MAX_CHARS))
            return

        if cls._execute_db_bool_request(lambda: DbMemo.edit_memo(message.author.id,
                                                                 name_executor.get_text(),
                                                                 add_content),
                                        message):
            cls._reply(message, "Mémo [**{}**] édité !".format(name_executor.get_text()))

    @classmethod
    def _get_memo(cls, message: Message, name_executor: TextParamExecutor):
        memo = DbMemo.get_memo(message.author.id, name_executor.get_text())
        if memo:
            cls._reply(message,
                       AppMessages.get_memo_embed(memo.name, memo.content),
                       20)
        else:
            cls._display_error(message, "Aucun nom de mémo avec le terme `{}`.".format(
                name_executor.get_text()))

    # noinspection PyUnusedLocal
    @classmethod
    def _get_memo_line(cls, message: Message, name_executor: TextParamExecutor, line_executor: FixedValueParamExecutor,
                       int_executor: IntParamExecutor):
        memo = DbMemo.get_memo(message.author.id, name_executor.get_text())

        if not memo:
            cls._display_error(message, "Aucun nom de mémo avec le terme `{}`.".format(
                name_executor.get_text()))
            return

        line_position = int_executor.get_int()
        line_count = ParsingUtils.count_lines(memo.content)
        # remove bullet and space at begin of line
        line = ParsingUtils.get_line(memo.content, line_position - 1)
        line = re.sub(r"^`\d+`\s+", "", line)

        if not line:
            cls._display_error(message,
                               "Le mémo [**{}**] n'a que `{}` lignes.".format(name_executor.get_text(),
                                                                              line_count))
            return

        cls._reply(message, AppMessages.get_memo_line_embed(line))

    # @classmethod
    # def _get_memo_by_position(cls, message: Message, int_executor: IntParamExecutor):
    #     memo = DbMemo.get_memo_by_position(message.author.id, int_executor.get_int())
    #     if memo:
    #         cls._reply(message,
    #                    AppMessages.get_memo_embed(memo.name, memo.content),
    #                    20)
    #     else:
    #         cls._display_error(message, "Aucun mémo avec le numéro `{}`.".format(
    #             int_executor.get_int()))

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
            # Replace spaces with unbreakable so memo titles containing space are not wrapped.
            # memos = ["`" + memo.replace(" ", "\u00A0") + "`" for memo in memos]
            memo_list_str = []
            for memo in memos:
                # With memo number
                # memo_list_str.append("{}: `{}`".format(memo.position,
                #                                        memo.name.replace(" ", "\u00A0")
                #                                        )
                #                      )
                memo_list_str.append("`{}`".format(memo.name.replace(" ", "\u00A0")))

            cls._reply(message,
                       AppMessages.get_memo_embed("Mes mémos",
                                                  "\u00A0\u0020\u00A0".join(memo_list_str),
                                                  "{} / {}".format(len(memos), cls._MAX_PER_USER)
                                                  ),
                       20
                       )
        # \u00A0\u0020\u00A0 : 2 unbreakable spaces to keep margin, and 1 normal space to wrap line between 2 titles
