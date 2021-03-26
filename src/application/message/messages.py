from discord import Embed

from core.utils.parsing_utils import ParsingUtils


class AppMessages:
    _HOOK_EMBED_COLOR = 0x17907e

    @classmethod
    def get_hook_embed(cls, title: str = None, description: str = None) -> Embed:
        return Embed(title=title, description=description, color=cls._HOOK_EMBED_COLOR)

    @classmethod
    def get_recorded_message_embed(cls, content: str, target_id: int,
                                   author_name: str = None) -> Embed:
        # TODO : il faudrait utiliser format_links en y ajoutant le gras
        extracts = ParsingUtils.extract_links(content)

        user_message = "**" + extracts.message + "**" if extracts.message else ""

        description = "{user_message} <@{target_id}>{message_links_sep}{links}".format(
            user_message=user_message,
            target_id=target_id,
            message_links_sep="\n" if extracts.links else "",
            links="\n".join(extracts.links)
        )

        embed = cls.get_hook_embed(description=description)

        if author_name:
            embed.set_footer(text=f"Signé {author_name}")

        return embed

    @staticmethod
    def get_memo_embed(title: str, content: str, footer: str = None) -> Embed:
        embed = Embed(title=f"Mémo [{title}]",
                      description=content,
                      color=0x594566)
        if footer:
            embed.set_footer(text=footer)

        return embed
