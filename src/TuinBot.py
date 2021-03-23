from discord import Intents

from application.commands.reac_command import AutoReactionCommand
from application.commands.reply_command import ReplyMessageCommand
from application.commands.spoil_command import AutoSpoilerCommand
from application.commands.tuin_command import TuinBotCommand
from application.commands.typing_mess_command import TypingMessageCommand
from core.client.bot import DiscordBot
from core.command.repository import CommandRepository
from core.data.properties import AppProperties

IS_BETA = False

PROPERTIES_PATH = "../data/bot.properties"
BETA_PROPERTIES_PATH = "../data/bot-beta.properties"

AppProperties.load(BETA_PROPERTIES_PATH if IS_BETA else PROPERTIES_PATH)

CommandRepository.set_command_list(TuinBotCommand,
                                   AutoReactionCommand,
                                   AutoSpoilerCommand,
                                   TypingMessageCommand,
                                   ReplyMessageCommand)

intents = Intents.default()
intents.members = True
intents.typing = True
# intents.presences = True
# AppProperties

bot = DiscordBot(activity_name=TuinBotCommand.name(), intents=intents)
bot.run(AppProperties.bot_token())
