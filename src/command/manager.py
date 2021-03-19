from discord import Message, Client

from command.command_base import Commands
from command.factory import CommandFactory
from command.types import HookType


class CommandManager:

    @classmethod
    def manage_message(cls, message: Message, client: Client):
        if message.author.bot:
            return

        cls._parse_command(message, client)

        for hook in Commands.get_hooks(HookType.MESSAGE):
            hook.execute_hook(message)

    @staticmethod
    def _parse_command(message: Message, client: Client):
        content = message.content

        # Dunno when, but we can have a zero length message (maybe when a new user join the channel ?)
        if not content:
            return

        if content[0] != "!":
            return

        if len(content) < 2:
            return

        command_split = content[1:].split()
        command_name = command_split[0]

        command = CommandFactory.get_command(command_name)

        if not command:
            return

        command.execute(message, command_split[1:], client)
