from typing import List, Union

from discord import Embed

from command.command_base import BaseCommand, Commands
from command.params.syntax import CommandSyntax


class TuinBotCommand(BaseCommand):

    @staticmethod
    def name() -> str:
        return "tuin"

    @staticmethod
    def description() -> str:
        return "Affiche les commandes disponibles pour les tuins."

    @classmethod
    def _build_syntaxes(cls) -> List[CommandSyntax]:
        return []

    @classmethod
    def get_help(cls) -> Union[Embed, str]:
        desc = "Ici on prend soin de nos tuins et on leur donne des " \
               "commandes débiles pour se troller mutuellement.```apache"
        for command in Commands.LIST:
            desc += "\n!%s : %s" % (command.name(), command.description())
        desc += "```\nTape une commande pour voir sa page d'aide."

        help_mess = Embed(title="Commandes disponibles pour les tuins",
                          description=desc, color=0x967b29)

        return help_mess
