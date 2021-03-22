from datetime import datetime
from typing import Union

from discord import Client, Game, Message, User, Member
from discord.abc import Messageable

from command.commands.tuin_command import TuinBotCommand
from command.manager import CommandManager


class TuinBot(Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(activity=Game("!" + TuinBotCommand.name()))

    async def on_message(self, message: Message):
        CommandManager.manage_message(message, self)

    async def on_typing(self, channel: Messageable, user: Union[User, Member], when: datetime):
        CommandManager.manage_typing(channel, user, when)
