import time
import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient
import pymongo
import io
import os
import requests
from datetime import datetime

from core.mod import *
from core.dbs import *
from core.enums import *
from core.bot_model import SupportBot
from Functions.Checker import *

from Buttons.verify_buttons import *
from Functions.dicts import *


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot: SupportBot = bot
        self.cid_to_rating__dict = {"one_point": 1, "two_point": 2, "three_point": 3, "four_point": 4, "five_point": 5}

        self.check_timeout_feedback.start()
        self.check_remove_not_verify.start()

    @tasks.loop(seconds=10)
    async def check_remove_not_verify(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(ClientInfo.BOT_GUILD_ID)
        for find in list(not_verify.find({"time_end": {"$lte": int(time.time())}})):
            not_verify.delete_one(find)
            if user := guild.get_member(find['member_id']):
                await user.remove_roles(guild.get_role(RolesInfo.DENY_VERIFY_ROLE))
                emb = disnake.Embed(
                    title='Недопуск',
                    description=f'**Вам был снят недопуск.**\n'
                                f'теперь вы снова **можете** пройти **верификацию** на сервере **ознакомившись с памяткой** в канале \"Информация\"',
                    colour=0x2f3136
                )
                try:
                    await user.send(embed=emb)
                except full_errors:
                    pass

    @tasks.loop(seconds=25)
    async def check_timeout_feedback(self):
        await self.bot.wait_until_ready()
        for find in list(feedback_db.find({"time_end": {"$lte": int(time.time())}})):
            feedback_db.delete_one(find)
            if user := await self.bot.fetch_user(find['member_id']):
                dm_channel = user.dm_channel or await user.create_dm()
                if msg := await dm_channel.fetch_message(find['msg_id']):
                    try:
                        await msg.edit(components=[])
                    except full_errors:
                        pass

    @commands.slash_command(
        name='verify',
        description=f'Верифицировать пользователя',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description=f'Укажите пользователя, которого требуется верифицировать',
                required=True,
                type=disnake.OptionType.user
            )
        ]
    )
    async def verify_command(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member):
        await interaction.response.defer()
        find = support_db.find_one({"member_id": member.id})
        
        if staff_check(member):
            return await interaction.send(
            embed = disnake.Embed(description=f'Произошла ошибка! Вы не можете выполнить эту команду над этим пользователем!', colour=0x2f3136), ephemeral=True)
        if member and member.bot:
            return await interaction.send(embed = disnake.Embed(description='Данная команда **недоступна** для применения на **ботов**!'), colour=0x2f3136, ephemeral=True)
        if not find:
            support_db.insert_one(generate_support_profile_post(guild=interaction.guild, member=member))
        emb = disnake.Embed(
            title=f'Верификация',
            description=f'{interaction.author.mention}, **выберите** действие с пользователем {member.mention}!',
            color=0x2f3136
        ) \
            .set_thumbnail(url=interaction.author.display_avatar.url) \
            .set_footer(text=f'ID: {member.id}')
        emb.add_field(name=f'> Аккаунт создан:',
                      value=f'```{datetime.fromtimestamp(int(member.created_at.timestamp())).strftime("%d.%m.%Y")}```')
        emb.add_field(name=f'> Зашел на сервер:',
                      value=f'```{datetime.fromtimestamp(int(member.joined_at.timestamp())).strftime("%d.%m.%Y")}```')
        btns = VerifyButtons(author=interaction.author, bot=self.bot, user=member)
        btns.msg = await interaction.edit_original_message(embed=emb, view=btns)

    @commands.Cog.listener("on_button_click")
    async def feedback_listener(self, inter: disnake.MessageInteraction):
        cid = str(str(inter.component.custom_id).split('__')[0])
        if cid in ['one_point', "two_point", 'three_point', "four_point", 'five_point']:
            find = feedback_db.find_one({"msg_id": inter.message.id})
            if not find:
                return await inter.send(
                    embed=disnake.Embed(description=f'Произошла ошибка! Повторите попытку!', colour=0x2f3136),
                    ephemeral=True)

            await inter.response.send_modal(
                title="Отзыв на Проверяющего",
                custom_id=f"feedback_modal__{cid}",
                components=[
                    disnake.ui.TextInput(
                        label=f"Отзыв с оценкой: {self.cid_to_rating__dict[cid]}",
                        placeholder="Оцените работу проверяющего!",
                        custom_id="content",
                        style=disnake.TextInputStyle.paragraph,
                        min_length=3,
                        max_length=150,
                    )
                ]
            )

    @commands.Cog.listener("on_modal_submit")
    async def modal_listener(self, inter: disnake.ModalInteraction):
        cid = str(str(inter.custom_id).split('__')[1])
        if cid in ['one_point', 'two_point', 'three_point', 'four_point', 'five_point']:
            rating = self.cid_to_rating__dict[cid]
            comment = inter.text_values['content']
            find = feedback_db.find_one({"msg_id": inter.message.id})
            if not find:
                return await inter.send(
                    embed=disnake.Embed(description=f'Произошла ошибка! Повторите попытку!', colour=0x2f3136),
                    ephemeral=True)

            emb = disnake.Embed(
                title='Добро пожаловать на сервер!',
                description=f'{inter.author.mention}, **благодарим** Вас за отзыв, нам **очень приятно**!',
                colour=0x2f3136
            )
            await inter.response.edit_message(embed=emb, components=[])

            emb = disnake.Embed(
                title='Новый отзыв',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=inter.author.display_avatar.url)
            emb.add_field(name='Пользователь:',
                          value=f'· {inter.author.mention}\n'
                                f'· {inter.author}\n'
                                f'· ID: {inter.author.id}\n', inline=False)
            emb.add_field(name='Оценка:', value=f'```{rating}/5```', inline=False)
            emb.add_field(name='Содержание:', value=f'```{comment}```', inline=False)
            support = self.bot.get_guild(ClientInfo.BOT_GUILD_ID).get_member(find['support_id'])
            emb.set_footer(text=f'Верифицировал(а): {support} | ID: {support.id}', icon_url=support.display_avatar.url)
            await self.bot.get_channel(ChannelsInfo.FEEDBACK_CHANNEL).send(embed=emb)
            feedback_db.delete_one(find)
            support_db.update_one(
                {"member_id": support.id, "guild_id": inter.guild_id},
                {"$set": {"status": "verified"}}
                )


def setup(bot):
    bot.add_cog(Verify(bot))
    print('Ког: "Верификация" загрузился!')
