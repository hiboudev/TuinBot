import re
import shlex
from datetime import datetime
from typing import Union

from discord import Message, Client, TextChannel, User, Member
from discord.abc import Messageable

from core.command.factory import CommandFactory
from core.command.repository import CommandRepository
from core.command.types import HookType


class CommandManager:
    _remove_bound_quotes_reg = re.compile(r"^\"(.*?)\"$", re.DOTALL)

    @classmethod
    def manage_message(cls, message: Message, client: Client):
        if message.author.bot:
            return

        # Guild is not always known (maybe in private messages), but our command needs a guild.
        if not message.guild:
            return

        if not isinstance(message.channel, TextChannel):
            return

        if not cls._parse_command(message, client):
            # we don't apply hooks on a command message
            for hook in CommandRepository.get_hooks(HookType.MESSAGE):
                # stop if a hook deletes the user message
                if hook.execute_message_hook(message):
                    break

    # noinspection PyUnusedLocal
    @classmethod
    def manage_typing(cls, channel: Messageable, user: Union[User, Member], when: datetime):
        if user.bot:
            return

        # Note: In a TextChannel, user is a Member
        if not isinstance(channel, TextChannel):
            return

        if not user.guild:
            return

        for hook in CommandRepository.get_hooks(HookType.TYPING):
            hook.execute_typing_hook(channel, user)

    @classmethod
    def _parse_command(cls, message: Message, client: Client) -> bool:
        content = message.content

        # Dunno when, but we can have a zero length message (maybe when a new user join the channel ?)
        if not content:
            return False

        if content[0] != "!":
            return False

        if len(content) < 2:
            return False

        # Use quotes to insert spaces in a parameter value
        command_split = [
            cls._remove_bound_quotes_reg.sub(r"\g<1>", i)
            for i in shlex.split(content[1:], posix=False)
        ]
        command_name = command_split[0]

        command = CommandFactory.get_command(command_name)

        if not command:
            return False

        command.execute(message, command_split[1:], client)

        return True
