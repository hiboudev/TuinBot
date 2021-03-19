from discord import Client, Message, Intents, CustomActivity, Game

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

bot = TuinBot(intents=intents)
bot.run('ODIxNjkzMDAyMDAzMTIwMTY4.YFHbPQ.KDFkxtixXQ0IsonxgGMC0TiNNF8')
