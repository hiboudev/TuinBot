from discord import Client, Message, Intents, Game

from command.command_base import Commands
from command.commands.reac_command import AutoReactionCommand
from command.commands.spoil_command import AutoSpoilerCommand
from command.commands.tuin_command import TuinBotCommand
from command.manager import CommandManager
from data.properties import AppProperties

Commands.set_command_list(TuinBotCommand,
                          AutoReactionCommand,
                          AutoSpoilerCommand)


class TuinBot(Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(activity=Game("!" + TuinBotCommand.name()))

    async def on_message(self, message: Message):
        CommandManager.manage_message(message, self)


intents = Intents.default()
intents.members = True
intents.typing = True
# intents.presences = True
# AppProperties

bot = TuinBot(intents=intents)
bot.run(AppProperties.bot_token())
