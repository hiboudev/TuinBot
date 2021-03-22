from discord import Intents

from client.bot import TuinBot
from command.command_base import Commands
from command.commands.reac_command import AutoReactionCommand
from command.commands.reply_command import ReplyMessageCommand
from command.commands.spoil_command import AutoSpoilerCommand
from command.commands.tuin_command import TuinBotCommand
from command.commands.typing_mess_command import TypingMessageCommand
from data.properties import AppProperties

IS_BETA = True

PROPERTIES_PATH = "../data/bot.properties"
BETA_PROPERTIES_PATH = "../data/bot-beta.properties"

AppProperties.load(BETA_PROPERTIES_PATH if IS_BETA else PROPERTIES_PATH)

Commands.set_command_list(TuinBotCommand,
                          AutoReactionCommand,
                          AutoSpoilerCommand,
                          TypingMessageCommand,
                          ReplyMessageCommand)

intents = Intents.default()
intents.members = True
intents.typing = True
# intents.presences = True
# AppProperties

bot = TuinBot(activity_name=TuinBotCommand.name(), intents=intents)
bot.run(AppProperties.bot_token())
