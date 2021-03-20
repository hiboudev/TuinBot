# from __future__ import annotations
from typing import List

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
    def get_help(cls) -> str:
        help_mess = "Commandes disponibles :"

        for command in Commands.LIST:
            help_mess += "\n**!%s** : %s" % (command.name(), command.description())
        help_mess += "\nTape une commande pour voir sa page d'aide."

        return help_mess
