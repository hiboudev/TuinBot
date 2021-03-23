from jproperties import Properties


class AppProperties:
    _config: Properties

    @classmethod
    def load(cls, path: str):
        cls._config = Properties()

        with open(path, 'rb') as config_file:
            cls._config.load(config_file)

        is_beta = cls._config.get("is_beta").data
        if is_beta != "0" and is_beta != "1":
            raise Exception("Config 'is_beta' should be 0 or 1")

        print("Using config %s!" % "Beta" if cls.is_beta() else "Release")

    @classmethod
    def is_beta(cls) -> bool:
        return cls._config.get("is_beta").data == "1"

    @classmethod
    def bot_token(cls) -> str:
        if cls.is_beta():
            return cls._config.get("bot_token_beta").data

        return cls._config.get("bot_token").data

    @classmethod
    def db_name(cls) -> str:
        return cls._config.get("db_name").data

    @classmethod
    def db_host(cls) -> str:
        return cls._config.get("db_host").data

    @classmethod
    def db_user(cls) -> str:
        return cls._config.get("db_user").data

    @classmethod
    def db_password(cls) -> str:
        return cls._config.get("db_password").data
