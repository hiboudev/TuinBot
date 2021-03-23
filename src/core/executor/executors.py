from typing import Union

from discord import Message, TextChannel, User, Client

from core.executor.base import CommandParamExecutor
from core.param.params import CommandParam, IntParamConfig
from core.utils.parsing_utils import ParsingUtils


class UserParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._user = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> bool:
        return True

    def _process_param(self, value: str, message: Message, client: Client) -> bool:
        if not isinstance(message.channel, TextChannel):
            return False

        # TODO ce serait bien de stocker les min/max sur le param,
        # mais comment bien gérer la doc selon si c'est un chiffre ou un string ?
        if len(value) < 3:
            return self._set_error("Le nom d'utilisateur doit faire au moins 3 caractères.")

        self._user = ParsingUtils.find_user(message.channel.members, value)

        if self._user:
            return True
        else:
            return self._set_error("Utilisateur introuvable.")

    def get_user(self) -> Union[User, None]:
        return self._user


class EmojiParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._emoji = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> bool:
        return True

    def _process_param(self, value: str, message: Message, client: Client) -> bool:
        self._emoji = ParsingUtils.get_emoji(value, client)

        if self._emoji:
            return True
        else:
            return self._set_error("Emoji invalide.")

    def get_emoji(self) -> Union[str, None]:
        return self._emoji


class FixedValueParamExecutor(CommandParamExecutor):

    @staticmethod
    def always_validate_input_format() -> bool:
        return False

    def _validate_input_format(self, value: str) -> bool:
        return value == self.param.name

    def _process_param(self, value: str, message: Message, client: Client) -> bool:
        if value == self.param.name:
            return True
        else:
            return self._set_error("Valeur invalide.")


class IntParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._int_value = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return False

    def _validate_input_format(self, value: str) -> bool:
        try:
            self._int_value = int(value)
            return True
        except ValueError:
            return False

    def _process_param(self, value: str, message: Message, client: Client) -> bool:
        if self.param.config is None or not isinstance(self.param.config, IntParamConfig):
            raise Exception("Config not found!")

        if self.param.config.min_value <= self._int_value <= self.param.config.max_value:
            return True
        else:
            return self._set_error("Valeur invalide.")

    def get_int(self) -> int:
        return self._int_value


class TextParamExecutor(CommandParamExecutor):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._text = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> bool:
        return True

    def _process_param(self, value: str, message: Message, client: Client) -> bool:
        self._text = value
        return True

    def get_text(self) -> str:
        return self._text
