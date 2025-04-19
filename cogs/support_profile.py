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

from Functions.TimeConvent import *
from Functions.Checker import *
from Functions.dicts import *

from Buttons.support_profile_buttons import *

from core.bot_model import SupportBot


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot: SupportBot = bot

        # self.vacation_end_check.start()
        self.week_end_check.start()
        self.day_end_check.start()

    # @tasks.loop(seconds=10)
    # async def vacation_end_check(self):
    #     await self.bot.wait_until_ready()
    #     guild = self.bot.get_guild(ClientInfo.BOT_GUILD_ID)
    #     for find in list(vacation_db.find({"guild_id": guild.id, "status": True, "time_end": {"$lte": int(time.time())}})):
    #         emb = disnake.Embed(
    #             title='Отпуск - Support',
    #             description=f'Ваш отпуск **закончился**!\n\n'
    #                         f'> У вас есть освобождение от **недельной нормы** если ваш отпуск закончился в **середине** недели.',
    #             colour=0x2f3136
    #         )
    #         emb.set_footer(text='Удачной работы!')
    #         member = guild.get_member(find['member_id'])
    #         try:
    #             await member.send(embed=emb, content=f'{member.mention}')
    #         except full_errors:
    #             pass
    #         vacation_db.delete_one(find)
    #         support_db.update_one({"member_id": find['member_id'], "guild_id": guild.id},
    #                               {"$set": {"vacation": 0}})

    @tasks.loop(seconds=5)
    async def week_end_check(self):
        await self.bot.wait_until_ready()
        find = staff_db.find_one({"guild_id": ClientInfo.BOT_GUILD_ID})

        if find is not None:
            time_start = int(time.time())
            if 'reset_week_support' in find and time_start >= find['reset_week_support']:
                support_db.update_many({"guild_id": ClientInfo.BOT_GUILD_ID}, {"$set": {"verify_week": 0, "voice_week": 0}})

    @tasks.loop(seconds=5)
    async def day_end_check(self):
        await self.bot.wait_until_ready()
        find = staff_db.find_one({"guild_id": ClientInfo.BOT_GUILD_ID})
        if find is None:
            staff_db.insert_one({"guild_id": ClientInfo.BOT_GUILD_ID, "reset_day_support": int(time.time()) + (60 * 60 * 24 * 7)})
            find = staff_db.find_one({"guild_id": ClientInfo.BOT_GUILD_ID})
        time_start = int(time.time())
        if time_start >= find['reset_day_support']:
            support_db.update_many({"guild_id": ClientInfo.BOT_GUILD_ID},
                                   {"$set": {"voice_day": 0}})

            staff_db.update_one({"guild_id": ClientInfo.BOT_GUILD_ID},
                                {"$inc": {"reset_day_support": (60 * 60 * 24 * 7) - (int(time.time()) - time_start)}})


    @commands.slash_command(
        name='sprofile',
        description='Открыть профиль Проверяющего',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя для просмотра его профиля',
                required=False,
                type=disnake.OptionType.user
            )
        ]
    )
    async def support_profile_command(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        if not member:
            member = interaction.author

        if not support_check(member): return await interaction.edit_original_message(embed=disnake.Embed(
            description=f'Пользователь {member.mention} **не** является частью модерации!', colour=0x2f3136
        ))
        find = support_db.find_one({"member_id": member.id})
        if not find:
            support_db.insert_one(generate_support_profile_post(guild=interaction.guild, member=member))
            find = support_db.find_one({"member_id": member.id})

        emb = disnake.Embed(
            title=f'Профиль проверяющего - {member}',
            colour=0x2f3136
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        if member.id != interaction.author.id:
            emb.set_footer(text=f'Вызвал(а): {interaction.author}', icon_url=interaction.author.display_avatar.url)

        emb.add_field(name='Активность:', value=f'```{convert_time(find["voice"])}```')
        # emb.add_field(name='Баллы:', value=f'```{find["points"]}```')
        # emb.add_field(name='Оценка:', value=f'```{get_support_rating(find)}/5```')  # доделать в будущем!

        emb.add_field(name='Верификаций:', value=f'```{find["verify_week"]} ({find["verify"]})```')  # доделать за неделю
        # emb.add_field(name='Выговоров:', value=f'```{find["warns"]}/3```')
        # emb.add_field(name='Отпуск:', value=f'```{yes_no_dict[find["vacation"]]}```')

        # emb.add_field(name='Прайм-Актив:', value=f'```{convert_time(find["prime_voice"])}```')
        # emb.add_field(name='Прайм-Тайм', value=f'```{dict_prime_times[find["prime_time"]]}```')

        btns = SProfileButtons(bot=self.bot, author=interaction.author, member=member)

        await interaction.edit_original_message(embed=emb, view=btns)

    # @commands.Cog.listener("on_button_click")
    # async def feedback_listener(self, inter: disnake.MessageInteraction):
    #     if inter.component.custom_id == "accept_vacation":
    #         emb = inter.message.embeds[0].set_footer(text=f'Одобрил(а): {inter.author} | ID: {inter.author.id}', icon_url=inter.author.display_avatar.url)
    #         await inter.response.edit_message(embed=emb, components=[])

    #         find = vacation_db.find_one({"msg_id": inter.message.id})
    #         emb = disnake.Embed(
    #             title='Отпуск - Support',
    #             description=f'Ваш отпуск был **Одобрен**!',
    #             colour=0x2f3136
    #         )
    #         emb.set_footer(text='Удачного отдыха!')
    #         member = inter.guild.get_member(find['member_id'])
    #         try:
    #             await member.send(embed=emb, content=f'{member.mention}')
    #         except full_errors:
    #             pass
    #         await member.add_roles(inter.guild.get_role(RolesInfo.VACATION_ROLE))
    #         vacation_db.update_one({"msg_id": inter.message.id}, {"$set": {"time_end": int(time.time()) + find['time_seconds'], "status": True,
    #                                                                        "author_id": inter.author.id}})
    #         support_db.update_one({"member_id": find['member_id'], "guild_id": inter.guild.id}, {"$set": {"vacation": 1}})
    #     elif inter.component.custom_id == "deny_vacation":
    #         emb = inter.message.embeds[0].set_footer(text=f'Отклонил(а): {inter.author} | ID: {inter.author.id}',
    #                                                  icon_url=inter.author.display_avatar.url)
    #         await inter.response.edit_message(embed=emb, components=[])

    #         find = vacation_db.find_one({"msg_id": inter.message.id})
    #         emb = disnake.Embed(
    #             title='Отпуск - Support',
    #             description=f'Ваш отпуск был **Отклонён**!',
    #             colour=0x2f3136
    #         )
    #         emb.set_footer(text=f'Отклонил(а): {inter.author} | ID: {inter.author.id}',
    #                                                  icon_url=inter.author.display_avatar.url)
    #         member = inter.guild.get_member(find['member_id'])
    #         try:
    #             await member.send(embed=emb, content=f'{member.mention}')
    #         except full_errors:
    #             pass
    #         vacation_db.delete_one(find)


def setup(bot):
    bot.add_cog(Profile(bot))
    print('Ког: "Профиль саппорта" загрузился!')
