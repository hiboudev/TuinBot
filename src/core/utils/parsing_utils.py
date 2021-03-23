import re
from dataclasses import dataclass
from typing import List

from discord import User, Client
from emoji import emoji_lis
from unidecode import unidecode

from core.utils.utils import Utils


@dataclass
class LinkExtract:
    message: str
    links: List[str]


class ParsingUtils:
    _link_reg_ex = re.compile(r"(http[s]?://[^\s]+)")
    _emoji_reg_ex = re.compile(r"^(?P<emoji_string><:(?P<name>[^:]+):(?P<id>\d+)>)")

    @staticmethod
    def find_user(users: List[User], name_part: str) -> [User, None]:
        """Slow search, iterate over all users list, except if username == name_part
        But smarter cause it checks pertinence.
        """

        name_part = unidecode(name_part.lower())
        """ Ordre d'importance :
        * Est le display name
        * Pseudo démarre avec la recherche
        * % de match
        """
        sort_rule = (("is_account_name", False), ("starts_with", True), ("match", True))
        matches = []

        for user in users:
            if user.bot:
                continue

            display_name = unidecode(user.display_name.lower())
            username = unidecode(user.name.lower())

            match = None
            names_comparaison = []

            if name_part in display_name:
                names_comparaison.append(
                    UserSearchResult(user,
                                     len(name_part) / len(display_name),
                                     display_name.startswith(name_part),
                                     False)
                )
            if name_part in username:
                names_comparaison.append(
                    UserSearchResult(user,
                                     len(name_part) / len(username),
                                     username.startswith(name_part),
                                     True)
                )

            if names_comparaison:
                if len(names_comparaison) == 1:
                    match = names_comparaison[0]
                else:
                    match = Utils.multisort(names_comparaison, sort_rule)[0]

            if match:
                if match.match == 1:
                    return match.user

                matches.append(match)

        Utils.multisort(matches, sort_rule)

        if matches:
            return matches[0].user

        return None

    # Fast search, stop at first match, whatever it's begin or middle of name
    # @staticmethod
    # def find_user(users: List[User], name_part: str) -> [User, None]:
    #     lower_name_part = unidecode(name_part.lower())
    #
    #     # First search display name
    #     for user in users:
    #         if lower_name_part in unidecode(user.display_name.lower()):
    #             return user
    #     # Then search account name
    #     for user in users:
    #         if lower_name_part in unidecode(user.name.lower()):
    #             return user
    #
    #     return None

    @staticmethod
    def get_emoji(text: str, client: Client) -> [str, None]:
        emojis = emoji_lis(text, "en")

        if emojis:
            return emojis[0]["emoji"]

        return ParsingUtils.get_custom_emoji(text, client)

    @classmethod
    def get_custom_emoji(cls, text: str, client: Client) -> [str, None]:
        matches = cls._emoji_reg_ex.search(text)
        if matches:
            for emoji in client.emojis:
                if emoji.id == int(matches.group("id")):
                    return matches.group("emoji_string")

        return None

    @classmethod
    def extract_links(cls, text: str) -> LinkExtract:
        links = cls._link_reg_ex.findall(text)
        message = cls._link_reg_ex.sub("", text)

        return LinkExtract(message, links)

    @classmethod
    def format_links(cls, text: str) -> str:
        return cls._link_reg_ex.sub(r"\n\g<1>\n", text)

    @classmethod
    def is_unique_link(cls, text: str) -> bool:
        return cls._link_reg_ex.fullmatch(text) is not None


class UserSearchResult:

    def __init__(self, user: User, match: float, starts_with: bool, is_account_name: bool):
        self.user = user
        self.match = match
        self.starts_with = starts_with
        self.is_account_name = is_account_name

    def __str__(self):
        return "%s %f %s" % (self.user, self.match, self.starts_with)
