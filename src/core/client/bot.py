from datetime import datetime
from typing import Union

from discord import Client, Game, Message, User, Member
from discord.abc import Messageable

from core.command.manager import CommandManager


class DiscordBot(Client):

    def __init__(self, activity_name: str = None, **options):
        super().__init__(**options)
        self.activity_name = activity_name
        print("Starting Discord bot...")

    async def on_ready(self):
        print(f"Logged in as {self.user}!")
        await self.change_presence(activity=Game("!" + self.activity_name))

    async def on_message(self, message: Message):
        CommandManager.manage_message(message, self)

    # noinspection PyMethodMayBeStatic
    async def on_typing(self, channel: Messageable, user: Union[User, Member], when: datetime):
        CommandManager.manage_typing(channel, user, when)
