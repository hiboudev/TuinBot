from discord import Client, Message, Intents, CustomActivity, Game
from jproperties import Properties

from command.manager import CommandManager


class TuinBot(Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(activity=Game("!tuin"))

    async def on_message(self, message: Message):
        CommandManager.manage_message(message, self)


intents = Intents.default()
intents.members = True
intents.typing = True
# intents.presences = True

"""
Put your bot token in a file "bot.properties" :
token=XXX 
"""
config = Properties()
with open('bot.properties', 'rb') as config_file:
    config.load(config_file)

bot = TuinBot(intents=intents)
bot.run(config.get("token").data)
