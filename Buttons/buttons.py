import disnake

class ButtonBackToMenuClan(disnake.ui.View):
    msg: disnake.Message

    def __init__(self, bot: disnake.Client, author: disnake.Member):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author

    @disnake.ui.button(label='Назад', style=disnake.ButtonStyle.red, row=1)
    async def back_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        ...

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
