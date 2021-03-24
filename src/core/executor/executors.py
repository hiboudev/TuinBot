from typing import Union, Optional

from discord import Message, TextChannel, User, Client

from core.executor.base import CommandParamExecutor, ValueType
from core.param.params import CommandParam, IntParamConfig
from core.utils.parsing_utils import ParsingUtils


class UserParamExecutor(CommandParamExecutor[str]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._user = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> Optional[ValueType]:
        return value

    def _process_param(self, validated_value: ValueType, message: Message, client: Client) -> bool:
        if not isinstance(message.channel, TextChannel):
            return False

        # TODO ajouter une config optionnelle pour ce min value
        if len(validated_value) < 3:
            return self._set_error("Le nom d'utilisateur doit faire au moins 3 caractères.")

        self._user = ParsingUtils.find_user(message.channel.members, validated_value)

        if self._user:
            return True
        else:
            return self._set_error("Utilisateur introuvable.")

    def get_user(self) -> Union[User, None]:
        return self._user


class EmojiParamExecutor(CommandParamExecutor[str]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._emoji = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> Optional[ValueType]:
        return value

    def _process_param(self, validated_value: ValueType, message: Message, client: Client) -> bool:
        self._emoji = ParsingUtils.get_emoji(validated_value, client)

        if self._emoji:
            return True
        else:
            return self._set_error("Emoji invalide.")

    def get_emoji(self) -> Union[str, None]:
        return self._emoji


class FixedValueParamExecutor(CommandParamExecutor[str]):

    @staticmethod
    def always_validate_input_format() -> bool:
        return False

    def _validate_input_format(self, value: str) -> Optional[ValueType]:
        if value == self.param.name:
            return value
        return None

    def _process_param(self, validated_value: ValueType, message: Message, client: Client) -> bool:
        if validated_value == self.param.name:
            return True
        else:
            return self._set_error("Valeur invalide.")


class IntParamExecutor(CommandParamExecutor[int]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._int_value = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return False

    def _validate_input_format(self, value: str) -> Optional[ValueType]:
        try:
            self._int_value = int(value)
            return self._int_value
        except ValueError:
            return None

    def _process_param(self, validated_value: ValueType, message: Message, client: Client) -> bool:
        # if self.param.config is None or not isinstance(self.param.config, IntParamConfig):
        #     raise Exception("Config not found!")
        #
        # if self.param.config.min_value <= self._int_value <= self.param.config.max_value:
        #     return True
        # else:
        #     return self._set_error("Valeur invalide.")
        return self.is_input_format_valid()

    def get_int(self) -> int:
        return self._int_value


class TextParamExecutor(CommandParamExecutor[str]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._text = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> Optional[ValueType]:
        return value

    def _process_param(self, validated_value: ValueType, message: Message, client: Client) -> bool:
        self._text = validated_value
        return True

    def get_text(self) -> str:
        return self._text
