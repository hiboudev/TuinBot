from typing import Union, Optional

from discord import Message, TextChannel, User, Client

from core.executor.base import CommandParamExecutor, ValidatedType
from core.param.params import CommandParam
from core.utils.parsing_utils import ParsingUtils


class UserParamExecutor(CommandParamExecutor[str]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._user = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> Optional[ValidatedType]:
        return value

    def _process_param(self, validated_value: ValidatedType, message: Message, client: Client) -> bool:
        if not isinstance(message.channel, TextChannel):
            return False

        self._user = ParsingUtils.find_user(message.channel.members, validated_value)

        if self._user:
            return True
        else:
            return self._set_error("Utilisateur introuvable")

    def get_user(self) -> Union[User, None]:
        return self._user


class EmojiParamExecutor(CommandParamExecutor[str]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._emoji = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return True

    def _validate_input_format(self, value: str) -> Optional[ValidatedType]:
        return value

    def _process_param(self, validated_value: ValidatedType, message: Message, client: Client) -> bool:
        self._emoji = ParsingUtils.get_emoji(validated_value, client)

        if self._emoji:
            return True
        else:
            return self._set_error("Emoji invalide")

    def get_emoji(self) -> Union[str, None]:
        return self._emoji


class FixedValueParamExecutor(CommandParamExecutor[str]):

    @staticmethod
    def always_validate_input_format() -> bool:
        return False

    def _validate_input_format(self, value: str) -> Optional[ValidatedType]:
        if value == self.param.name:
            return value
        self._set_error("Valeur invalide")
        return None

    def _process_param(self, validated_value: ValidatedType, message: Message, client: Client) -> bool:
        if validated_value == self.param.name:
            return True
        else:
            return self._set_error("Valeur invalide")


class IntParamExecutor(CommandParamExecutor[int]):

    def __init__(self, param: CommandParam):
        super().__init__(param)
        self._int_value = None

    @staticmethod
    def always_validate_input_format() -> bool:
        return False

    def _validate_input_format(self, value: str) -> Optional[ValidatedType]:
        try:
            self._int_value = int(value)
            return self._int_value
        except ValueError:
            self._set_error("La valeur n'est pas un chiffre entier")
            return None

    def _process_param(self, validated_value: ValidatedType, message: Message, client: Client) -> bool:
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

    def _validate_input_format(self, value: str) -> Optional[ValidatedType]:
        return value

    def _process_param(self, validated_value: ValidatedType, message: Message, client: Client) -> bool:
        self._text = validated_value
        return True

    def get_text(self) -> str:
        return self._text
