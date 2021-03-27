import re


class Sanitizer:
    _user_name_reg = re.compile(r"([>`*_\-~|])")

    @classmethod
    def user_name(cls, user_name: str) -> str:
        return cls._user_name_reg.sub(r"\\\g<1>", user_name)

    @classmethod
    def user_name_special_quotes(cls, user_name: str) -> str:
        """
        Use this method when username is inserted between this quotes : `.
        """
        return user_name.replace("`", "'")
