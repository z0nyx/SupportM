import time
import disnake
import asyncio
from disnake.ext import commands
from Functions.TimeConvent import *

from core.enums import *
from core.dbs import *


class VerifyButtons(disnake.ui.View):
    msg: disnake.Message

    def __init__(self, bot: disnake.Client, author: disnake.Member, user: disnake.Member):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author
        self.user = user

        deny_verify_role = bot.get_guild(ClientInfo.BOT_GUILD_ID).get_role(RolesInfo.DENY_VERIFY_ROLE)
        if deny_verify_role in user.roles:  # если есть, значит ток снимаем
            self.block_verify_button.disabled = True
        else:  # нету? Смысл снимать. Выдавать можно только
            self.remove_block_verify_button.disabled = True

        new_role = bot.get_guild(ClientInfo.BOT_GUILD_ID).get_role(RolesInfo.NEW_ROLE)
        if new_role in user.roles:  # если чел новичок, смысл давать ему его снова?
            self.new_button.disabled = True
        else: # не новичок? Тогде мб вернём?)
            self.verify_button.disabled = True
            # self.girl_button.disabled = True

    @disnake.ui.button(label='Верефицировать', style=disnake.ButtonStyle.gray, row=1)
    async def verify_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        emb = disnake.Embed(
            title='Верификация',
            description=f'**Пользователь {self.user.mention} верифицирован {interaction.author.mention}**!'
        )
        emb.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.edit_message(embed=emb, view=None)
        await self.user.remove_roles(interaction.guild.get_role(RolesInfo.NEW_ROLE))

        emb_log = disnake.Embed(
            title='Верификация',
            colour=0x2f3136
        ).set_footer(text=f'Верифицировал(а): {interaction.author} | ID: {interaction.author.id}') \
            .add_field(name='Пользователь:',
                       value=f'· {self.user.mention}\n'
                             f'· {self.user}\n'
                             f'· ID: {self.user.id}\n', inline=False)
        await self.bot.get_channel(ChannelsInfo.VERIFY_LOGS_CHANNEL).send(embed=emb_log)

        emb = disnake.Embed(
            title='Добро пожаловать на сервер!',
            description=f'Вы можете **оценить** и оставить **краткий отзыв**, что-бы **улучшить** качество работы **Проверяющих**. '
                        f'На это вам даётся **5 минут!**\n'
        )
        emb.set_thumbnail(url=interaction.guild.icon.url)
        row = disnake.ui.ActionRow()
        row.add_button(label='1', custom_id=f'one_point__feedback_button', style=disnake.ButtonStyle.red)
        row.add_button(label='2', custom_id=f'two_point__feedback_button', style=disnake.ButtonStyle.red)
        row.add_button(label='3', custom_id=f'three_point__feedback_button', style=disnake.ButtonStyle.gray)
        row.add_button(label='4', custom_id=f'four_point__feedback_button', style=disnake.ButtonStyle.blurple)
        row.add_button(label='5', custom_id=f'five_point__feedback_button', style=disnake.ButtonStyle.green)

        try:
            msg = await self.user.send(embed=emb, components=[row])
        except full_errors:
            return

        feedback_db.insert_one({
            "guild_id": interaction.guild.id,
            "support_id": interaction.author.id,
            "member_id": self.user.id,
            "time_end": int(time.time()) + 60*5,
            "msg_id": msg.id
        })
        support_db.update_one({"member_id": interaction.author.id, "guild_id": interaction.guild.id},
                              {"$inc": {"verify": 1, "points": 1, "verify_week": 1}}, True)
    

    @disnake.ui.button(label='Недопуск', style=disnake.ButtonStyle.gray, row=1)
    async def block_verify_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(
            title="Выдача недопуска",
            custom_id="give_block_verify",
            components=[
                disnake.ui.TextInput(
                    label="Длительность (1D | 2D | 999Y)",
                    placeholder="Укажите длительность недопуска",
                    custom_id="latency",
                    style=disnake.TextInputStyle.short,
                    min_length=1,
                    max_length=10,
                ),
                disnake.ui.TextInput(
                    label="Причина",
                    placeholder="Укажите причину недопуска",
                    custom_id="reason",
                    style=disnake.TextInputStyle.paragraph,
                    min_length=5,
                    max_length=1024,
                )
            ]
        )
        try:
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "give_block_verify" and i.author.id == interaction.author.id,
                timeout=600,
            )
        except asyncio.TimeoutError:
            return

        latency = modal_inter.text_values["latency"]
        reason = modal_inter.text_values["reason"]

        if latency == '0':
            return await modal_inter.response.edit_message(
                embed=disnake.Embed(description=f'Длительность **не** может быть **0**!', colour=0x2f3136),
                view=None)

        try:
            time_seconds, name_russian, time_number = convert_to_russion(latency)
        except commands.BadArgument as e:
            return await modal_inter.response.edit_message(embed=disnake.Embed(description=f'При выполнении команды произошла ошибка: ```{e}```',
                                                              colour=0x2f3136), view=None)

        await self.user.add_roles(interaction.guild.get_role(RolesInfo.DENY_VERIFY_ROLE))
        emb = disnake.Embed(
            title='Недопуск',
            description=f'**Пользователю {self.user.mention} был выдан недопуск на {time_number} {name_russian} по причине:** {reason}\n',
            colour=0x2f3136
        )
        emb.set_footer(text=f'Верифицировал(а): {interaction.author} | ID: {interaction.author.id}',
                       icon_url=interaction.author.display_avatar.url)
        await modal_inter.response.edit_message(embed=emb, view=None)

        emb = disnake.Embed(
            title='Недопуск',
            description=f'**Вам был выдан недопуск на {time_number} {name_russian} по причине:** {reason}\n\n',
                        # f'**Выдал:** {interaction.author.mention}\n'
                        # f'· **ID:** {interaction.author.id}',
            colour=0x2f3136
        )
        emb.set_thumbnail(url=interaction.guild.icon.url)
        try:
            await self.user.send(embed=emb)
        except full_errors:
            pass

        post = {
            "guild_id": interaction.guild.id,
            "support_id": interaction.author.id,
            "member_id": self.user.id,
            "time_end": int(time.time()) + time_seconds,
            "reason": reason
        }
        not_verify.insert_one(post)

        emb_log = disnake.Embed(
            title='Недопуск',
            colour=0x2f3136
        ).set_footer(text=f'Верифицировал(а): {interaction.author} | ID: {interaction.author.id}') \
            .add_field(name='Пользователь:',
                       value=f'· {self.user.mention}\n'
                             f'· {self.user}\n'
                             f'· ID: {self.user.id}\n', inline=False) \
            .add_field(name='Причина:', value=f'```{reason}```')
        await self.bot.get_channel(ChannelsInfo.VERIFY_LOGS_CHANNEL).send(embed=emb_log)

    @disnake.ui.button(label='Снять недопуск', style=disnake.ButtonStyle.gray, row=1)
    async def remove_block_verify_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        emb_log = disnake.Embed(
            title='Снятие недопуска',
            colour=0x2f3136
        ).set_footer(text=f'Выполнил(а): {interaction.author} | ID: {interaction.author.id}') \
            .add_field(name='Пользователь:',
                       value=f'· {self.user.mention}\n'
                             f'· {self.user}\n'
                             f'· ID: {self.user.id}\n', inline=False)

        emb = disnake.Embed(
            title='Недопуск был снят!',
            description=f'Вы **сняли** недопуск пользователю {self.user.mention}!\n\n',
            colour=0x2f3136
        ).set_footer(text=f'Выполнил(а): {interaction.author} | ID: {interaction.author.id}',
                     icon_url=interaction.author.display_avatar.url)
        if find := not_verify.find_one({"member_id": self.user.id}):
            not_verify.delete_one(find)
            support = interaction.guild.get_member(find['support'])
            emb.description += f'**Недопуск был выдан:** {support.mention}\n' \
                               f'· **ID:** {support.id}'

            emb_log.add_field(name='Выдавал(а) недопуск:',
                              value=f'· {support.mention}\n'
                                    f'· {support}\n'
                                    f'· ID: {support.id}\n')
            emb_log.add_field(name='С причиной:', value=f'```{find["reason"]}```', inline=True)
        await interaction.response.edit_message(embed=emb, view=None)

        await self.user.remove_roles(interaction.guild.get_role(RolesInfo.DENY_VERIFY_ROLE))

        emb = disnake.Embed(
            title='Недопуск',
            description=f'**Вам был снят недопуск.**\n'
                        f'теперь вы снова **можете** пройти **верификацию** на сервере **ознакомившись с памяткой** в канале \"Информация\"',
            colour=0x2f3136
        )
        try:
            await self.user.send(embed=emb)
        except full_errors:
            pass

        await self.bot.get_channel(ChannelsInfo.VERIFY_LOGS_CHANNEL).send(embed=emb_log)
    
    @disnake.ui.button(label='Новичок', style=disnake.ButtonStyle.gray, row=1)
    async def new_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        new_role = interaction.guild.get_role(RolesInfo.NEW_ROLE)
        emb = disnake.Embed(
            title='Возвращение новичка',
            description=f"{interaction.author.mention}, Вы **успешно** вернули роль \"Новичка\" пользователю {self.user.mention}!",
            colour=0x2f3136
        )
        emb.set_thumbnail(url=interaction.author.display_avatar.url)
        await interaction.response.edit_message(embed=emb, view=None)

        await self.user.remove_roles(interaction.guild.get_role(RolesInfo.NEW_ROLE),
                                     interaction.guild.get_role(RolesInfo.NEW_ROLE))
        await self.user.add_roles(new_role)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if self.author != interaction.author:
            await interaction.send(
                embed=disnake.Embed(description=f'{interaction.author.mention}, у вас **нет** доступа к этому меню!',
                                    color=disnake.Color.from_rgb(47, 49, 54)), ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        if self.msg:
            try:
                await self.msg.delete()
            except (disnake.Forbidden, disnake.HTTPException, disnake.NotFound):
                pass
