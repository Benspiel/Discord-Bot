import discord
from discord.ext import commands

CHANNEL_ID = 1443699258778714152


class ToDoReasonModal(discord.ui.Modal):
    def __init__(self, cog: "ToDo", todo_message: discord.Message, action: str):
        title = "To-Do erledigen" if action == "done" else "To-Do ablehnen"
        super().__init__(title=title)
        self.cog = cog
        self.todo_message = todo_message
        self.action = action
        self.reason = discord.ui.TextInput(
            label="Begruendung",
            placeholder="Warum soll das To-Do so markiert werden?",
            required=True,
            max_length=500,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.todo_message.embeds:
            await interaction.response.send_message("Dieses To-Do hat kein Embed mehr.", ephemeral=True)
            return

        embed = self.todo_message.embeds[0]
        new_embed = self.cog.build_final_embed(
            embed=embed,
            action=self.action,
            member=interaction.user,
            reason=self.reason.value.strip(),
        )

        await self.todo_message.edit(embed=new_embed, view=ToDoView(self.cog, locked=True))
        await interaction.response.send_message("To-Do wurde aktualisiert.", ephemeral=True)


class ToDoView(discord.ui.View):
    def __init__(self, cog: "ToDo", locked: bool = False):
        super().__init__(timeout=None)
        self.cog = cog

        for item in self.children:
            item.disabled = locked

    @discord.ui.button(
        label="Erledigt",
        style=discord.ButtonStyle.success,
        custom_id="todo_done",
    )
    async def done_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.message is None:
            await interaction.response.send_message("Nachricht konnte nicht geladen werden.", ephemeral=True)
            return

        await interaction.response.send_modal(ToDoReasonModal(self.cog, interaction.message, "done"))

    @discord.ui.button(
        label="Ablehnen",
        style=discord.ButtonStyle.danger,
        custom_id="todo_reject",
    )
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.message is None:
            await interaction.response.send_message("Nachricht konnte nicht geladen werden.", ephemeral=True)
            return

        await interaction.response.send_modal(ToDoReasonModal(self.cog, interaction.message, "reject"))

    @discord.ui.button(
        label="In Bearbeitung",
        style=discord.ButtonStyle.secondary,
        custom_id="todo_progress",
    )
    async def progress_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.message is None or not interaction.message.embeds:
            await interaction.response.send_message("Dieses To-Do ist nicht mehr verfuegbar.", ephemeral=True)
            return

        new_embed = self.cog.build_progress_embed(interaction.message.embeds[0], interaction.user)
        await interaction.message.edit(embed=new_embed, view=ToDoView(self.cog))
        await interaction.response.send_message("To-Do ist jetzt in Bearbeitung.", ephemeral=True)


class ToDo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def build_final_embed(
        self,
        embed: discord.Embed,
        action: str,
        member: discord.abc.User,
        reason: str,
    ) -> discord.Embed:
        new_embed = embed.copy()
        new_embed.clear_fields()

        if action == "done":
            new_embed.color = discord.Color.green()
            status_text = "Erledigt"
        else:
            new_embed.color = discord.Color.red()
            status_text = "Abgelehnt"

        new_embed.add_field(name="Status", value=f"{status_text} von {member.mention}", inline=False)
        new_embed.add_field(name="Begruendung", value=reason, inline=False)
        return new_embed

    def build_progress_embed(
        self,
        embed: discord.Embed,
        member: discord.abc.User,
    ) -> discord.Embed:
        new_embed = embed.copy()
        new_embed.color = discord.Color.gold()
        new_embed.clear_fields()
        new_embed.add_field(name="Status", value=f"In Bearbeitung von {member.mention}", inline=False)
        return new_embed

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != CHANNEL_ID:
            return

        content = message.content.strip()
        if not content:
            return

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

        embed = discord.Embed(
            title="📌 Neues To-Do",
            description=content,
            color=discord.Color.blue(),
        )
        embed.set_footer(
            text=f"Eingereicht von {message.author}",
            icon_url=message.author.display_avatar.url,
        )

        await message.channel.send(embed=embed, view=ToDoView(self))


async def setup(bot):
    cog = ToDo(bot)
    bot.add_view(ToDoView(cog))
    await bot.add_cog(cog)
