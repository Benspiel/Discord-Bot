import discord
from discord.ext import commands
from discord import app_commands

ANNOUNCE_CHANNEL_ID = 1442440202332143617  # << HIER deinen Channel eintragen!
ROLE_ANNOUNCE = 1439602766304514158
ROLE_TEAM = 1442440202332143617


class AnnounceModal(discord.ui.Modal, title="Neue Ankündigung"):
    text = discord.ui.TextInput(
        label="Text der Ankündigung",
        style=discord.TextStyle.long,
        placeholder="Schreibe hier deine Nachricht rein...",
        required=True,
        max_length=4000
    )

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(ANNOUNCE_CHANNEL_ID)
        await channel.send(self.text.value)
        await interaction.response.send_message("✔️ Ankündigung gesendet!", ephemeral=True)


class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------
    # 1️⃣  /announce Befehl
    # ---------------------------
    @app_commands.command(name="announce", description="Sende eine Ankündigung in den Kanal.")
    async def announce(self, interaction: discord.Interaction):

        # Rollenprüfung
        roles = [r.id for r in interaction.user.roles]
        if ROLE_ANNOUNCE not in roles and ROLE_TEAM not in roles:
            return await interaction.response.send_message(
                "⛔ Du hast keine Berechtigung!", ephemeral=True
            )

        await interaction.response.send_modal(AnnounceModal(interaction))

    # ---------------------------
    # 2️⃣ Relay der Nachrichten
    # ---------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignoriere Bots
        if message.author.bot:
            return

        # Nur bestimmter Channel
        if message.channel.id != ANNOUNCE_CHANNEL_ID:
            return

        content = message.content

        # Nachricht löschen
        try:
            await message.delete()
        except:
            pass

        # Nachricht exakt senden (inkl. Zeilenumbrüche)
        await message.channel.send(content)


async def setup(bot):
    await bot.add_cog(Announce(bot))