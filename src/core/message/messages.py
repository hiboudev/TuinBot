from typing import Type

from discord import Embed

from core.command.types import Command
from core.param.params import ParamType


class Messages:
    nothing_to_do = "Il n'y a rien à faire."

    @staticmethod
    def build_help(command: Type[Command]) -> Embed:
        embed = Embed(title=f"Commande __{command.name()}__",
                      description="*%s*\n\u200B" % command.description(),
                      color=0x15659e)

        field_count = 0

        for syntax in command.get_syntaxes():
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

            # add space at field bottom for better lisibility (except for last line),
            #  it's thiner than an empty field.
            # add_bottom_margin = field_count < len(command.get_syntaxes()) - 2
            add_bottom_margin = True

            embed.add_field(name=syntax.title, inline=True,
                            value="""```ini\n!{name} {params}```{desc}{margin}""".format(
                                name=command.name(),
                                params=" ".join(params_syntax),
                                desc="\n".join(params_desc),
                                margin="\n\u200B" if add_bottom_margin else "")
                            )

            field_count += 1

            if field_count % 2 == 1:
                embed.add_field(name="\u200B", value="\u200B", inline=True)

        # embed.add_field(name="\u200B", value="\u200B", inline=False)

        details = command.description_details()
        if details:
            embed.set_footer(text=details)

        return embed
