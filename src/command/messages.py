from typing import Type

from discord import Embed

from command.params.params import ParamType
from command.types import Command


class Messages:
    @staticmethod
    def nothing_to_do() -> str:
        return "Il n'y a rien à faire."


class HelpMessageBuilder:

    def __init__(self, command: Type[Command]):
        self._command = command

    def build(self) -> Embed:
        embed = Embed(title="Commande __{name}__".format(name=self._command.name()),
                      description="*%s*\n\u200B" % self._command.description(),
                      color=0x15659e)

        field_count = 0

        for syntax in self._command.get_syntaxes():
            params_syntax = []
            params_desc = []

            for param in syntax.params:
                param_is_variable = param.param_type != ParamType.FIXED_VALUE

                if param_is_variable:
                    param_display_name = "[%s]" % param.name
                    params_desc.append("**%s** : %s" % (param_display_name, param.description))
                else:
                    param_display_name = "%s" % param.name

                params_syntax.append(param_display_name)

            add_bottom_margin = field_count < len(self._command.get_syntaxes()) - 2

            # add space at field bottom for better lisibility, it's thiner than an empty field
            embed.add_field(name=syntax.title, inline=True,
                            value="""```ini\n!{name} {params}```{desc}{margin}""".format(
                                name=self._command.name(),
                                params=" ".join(params_syntax),
                                desc="\n".join(params_desc),
                                margin="\n\u200B" if add_bottom_margin else "")
                            )

            field_count += 1

            if field_count % 2 == 1:
                embed.add_field(name="\u200B", value="\u200B", inline=True)

                # if field_count % 2 == 0 and field_count < len(self._command.get_syntaxes()):
                #     embed.add_field(name="\u200B", value="\u200B", inline=False)

        return embed
