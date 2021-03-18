import re
from typing import List

from discord import User, Client
from emoji import emoji_lis


class ParsingUtils:

    @staticmethod
    def find_user(users: List[User], name_part: str) -> [User, None]:
        lower_name_part = name_part.lower()

        # First search display name
        for user in users:
            if lower_name_part in user.display_name.lower():
                return user

        # Then search account name
        for user in users:
            if lower_name_part in user.name.lower():
                return user

        return None

    @staticmethod
    def get_emoji(text: str, client: Client) -> [str, None]:
        emojis = emoji_lis(text, "en")

        if not emojis:
            return ParsingUtils.get_custom_emoji(text, client)

        return emojis[0]["emoji"]

    @staticmethod
    def get_custom_emoji(text: str, client: Client) -> [str, None]:
        matches = re.search(r'^(?P<emoji_string><:(?P<name>[^:]+):(?P<id>\d+)>)', text)
        if matches:
            for emoji in client.emojis:
                if emoji.id == int(matches.group("id")):
                    return matches.group("emoji_string")

        return None
