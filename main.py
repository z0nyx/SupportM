import disnake
import os

from dotenv import load_dotenv

from core.bot_model import SupportBot

load_dotenv()
bot = SupportBot()

bot.run(os.getenv("TOKEN"))