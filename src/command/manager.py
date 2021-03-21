import shlex

from discord import Message, Client

from command.command_base import Commands
from command.factory import CommandFactory
from command.types import HookType


class CommandManager:

    @classmethod
    def manage_message(cls, message: Message, client: Client):
        if message.author.bot:
            return

        # Guild is not always known (maybe in private messages), but our commands needs a guild.
        if not message.guild:
            return

        # TODO bloquer tout ce qui vient pas d'un TextChannel ?

        if not cls._parse_command(message, client):
            # we don't apply hooks on a command message
            for hook in Commands.get_hooks(HookType.MESSAGE):
                hook.execute_hook(message)

    @staticmethod
    def _parse_command(message: Message, client: Client) -> bool:
        content = message.content

        # Dunno when, but we can have a zero length message (maybe when a new user join the channel ?)
        if not content:
            return False

        if content[0] != "!":
            return False

        if len(content) < 2:
            return False

        # Use quotes to insert spaces in a parameter value
        command_split = shlex.split(content[1:])
        command_name = command_split[0]

        command = CommandFactory.get_command(command_name)

        if not command:
            return False

        command.execute(message, command_split[1:], client)

        return True
