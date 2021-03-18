from discord import Client, Message, Intents

from command.manager import CommandManager


class TuinBot(Client):
    # instance = None

    # def __init__(self, **options):
    #     super().__init__(**options)
    #     TuinBot.instance = self

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: Message):
        print('Message from {0.author}: {0.content}'.format(message))
        CommandManager.manage_message(message, self)


intents = Intents.default()
intents.members = True
intents.typing = True
# intents.presences = True

bot = TuinBot(intents=intents)
bot.run('ODIxNjkzMDAyMDAzMTIwMTY4.YFHbPQ.KDFkxtixXQ0IsonxgGMC0TiNNF8')