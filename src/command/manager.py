from discord import Message, Client

from command.commands import HookType, Commands
from command.factory import CommandFactory


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
