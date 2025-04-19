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


class CommandsManage(commands.Cog):
    def __init__(self, bot):
        self.bot: SupportBot = bot

    @staticmethod
    def cogs_names():
        cogs_list = []
        for filename in os.listdir(f"./cogs"):
            if filename.endswith(".py"):
                cogs_list.append(disnake.OptionChoice(
                    name=f'{filename[:-3]}',
                    value=f'{filename[:-3]}'
                ))
        return cogs_list

    @commands.slash_command(
        name='reload',
        description='Перезагрузка файла бота',
        options=[disnake.Option(name='extension',
                                description="Название кога",
                                type=disnake.OptionType.string,
                                required=True,
                                choices=cogs_names())],
        default_member_permissions=disnake.Permissions(8),
        guild_ids=[ClientInfo.BOT_GUILD_ID])
    async def reload(self, interaction: disnake.ApplicationCommandInteraction, extension: str):
        if interaction.author.id not in [ClientInfo.ZONYX]:
            await interaction.send(f'Нет доступа к команде данного уровня!', ephemeral=True)
            return
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except:
            await interaction.send(f'Ког: **{extension}** -  **не** загружен!', ephemeral=True)
            return
        await interaction.send(f'Ког: **{extension}** Успешно перезагружен!', ephemeral=True)


def setup(bot):
    bot.add_cog(CommandsManage(bot))
    print('Ког: "Команды управления ботом" загрузился!')
