from jproperties import Properties


class AppProperties:
    _config: Properties

    @classmethod
    def load(cls):
        cls._config = Properties()
        with open('../data/bot.properties', 'rb') as config_file:
            cls._config.load(config_file)

    @classmethod
    def bot_token(cls) -> str:
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


AppProperties.load()
