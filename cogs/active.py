import disnake
from disnake.ext import commands, tasks
import asyncio

from core.dbs import *
from core.enums import *
from core.mod import *

from Functions.Checker import *
from Functions.dicts import *


class Activity(commands.Cog, name="active"):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        self.support_active_voice.start()

    @tasks.loop(seconds=60)
    async def support_active_voice(self):
        async def checks(member: disnake.Member, support_role: disnake.Role):
            if support_role in member.roles:
                find = support_db.find_one({"member_id": member.id})
                if not find:
                    support_db.insert_one(generate_support_profile_post(guild=member.guild, member=member))
                support_db.update_one({"member_id": member.id, "guild_id": member.guild.id}, {"$inc": {"voice": 1}}, True)
                find = support_db.find_one({"member_id": member.id, "guild_id": member.guild.id, "prime_time": {"$ne": 0}})
                if prime_time_checker(find['prime_time']):
                    support_db.update_one({"member_id": member.id, "guild_id": member.guild.id}, {"$inc": {"prime_voice": 1}})

        await self.bot.wait_until_ready()
        guild: disnake.Guild = self.bot.get_guild(ClientInfo.BOT_GUILD_ID)
        verify_category: disnake.CategoryChannel = guild.get_channel(ChannelsInfo.VERIFY_CATEGORY_ID)
        support_role = guild.get_role(RolesInfo.SUPPORT_ROLE)
        for channel in verify_category.voice_channels:
            for member in channel.members:
                asyncio.create_task(checks(member, support_role))

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        await member.add_roles(member.guild.get_role(RolesInfo.NEW_ROLE))


def setup(bot):
    bot.add_cog(Activity(bot))
    print('Ког: "Активность" загрузился!')
