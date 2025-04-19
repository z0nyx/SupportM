import os
import logging
import traceback

import disnake
from disnake.ext import commands

from core.enums import *

logging.basicConfig(
    filename='core/logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SupportBot(commands.InteractionBot):
    def __init__(self):
        intents = disnake.Intents.all()
        super().__init__(
            command_sync_flags=commands.CommandSyncFlags.all(),
            intents=intents,
            status=disnake.Status.idle,
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name="💗"
            )
        )

    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{filename[:-3]}")
                    logging.info(f'log: {filename} loaded')
                except Exception as error:
                    traceback.format_exc(error)

    async def on_ready(self):
        await self.wait_until_ready()
        print(f"Бот запущен")
        print(f'Вы вошли как {self.user}')
        self.load_cogs()
