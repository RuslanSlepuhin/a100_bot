import configparser
from bot.bot_handlers import BotHandlers

config = configparser.ConfigParser()
config.read("./settings/config.ini")
__token = config["BOT"]["token"]

if __name__ == "__main__":
    bot = BotHandlers(__token)
    bot.handlers()