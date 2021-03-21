from discord import Client, Game, Message

from command.commands.tuin_command import TuinBotCommand
from command.manager import CommandManager


class TuinBot(Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(activity=Game("!" + TuinBotCommand.name()))

    async def on_message(self, message: Message):
        CommandManager.manage_message(message, self)
