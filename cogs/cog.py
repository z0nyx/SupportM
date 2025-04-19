import time
import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient
import pymongo
import io
import os
import requests

from core.mod import *
from core.dbs import *
from core.enums import *

from core.bot_model import SupportBot


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot: SupportBot = bot


def setup(bot):
    bot.add_cog(Cog(bot))
    print('Ког: "КОГ" загрузился!')
