import discord
from discord.ext import commands

CHANNEL_ID = 1439614861536661615       # Verify-Channel
ROLE_ID = 1442204239630700676          # Rolle, die vergeben werden soll


# ---------- PERSISTENTE VIEW ----------
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verifizieren",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="verify_btn_persistent"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role is None:
            return await interaction.response.send_message(
                "❌ Die Verifizierungsrolle existiert nicht.", ephemeral=True
            )

        # Bot-Rollenposition prüfen
        bot_member = interaction.guild.get_member(interaction.client.user.id)
        if bot_member.top_role <= role:
            return await interaction.response.send_message(
                "❌ Ich kann diese Rolle nicht vergeben. Meine Rolle steht zu weit unten.",
                ephemeral=True
            )

        # Rolle geben
        try:
            await interaction.user.add_roles(role)
        except:
            return await interaction.response.send_message(
                "❌ Fehler beim Rollen vergeben. Bitte kontaktiere einen Admin.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "✅ Du wurdest erfolgreich verifiziert!",
            ephemeral=True
        )


# ---------- VERIFY-COG ----------
class VerifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(VerifyView())

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel is None:
            return

        # Channel leeren
        try:
            await channel.purge(limit=999)
        except:
            return

        # Embed
        embed = discord.Embed(
            title="📜 Server-Regeln",
            description=(
                "**1.** Achte auf deine Wortwahl und dein Verhalten.\n"
                "**2.** Keine beleidigenden, provozierenden oder pornografischen Inhalte.\n"
                "**3.** Stimmverzerrer nur mit Erlaubnis.\n"
                "**4.** Keine Aufnahme anderer Mitglieder ohne Zustimmung.\n"
                "**5.** Keine Werbung für andere Server oder Websites.\n"
                "**6.** Keine persönlichen Daten veröffentlichen.\n"
                "**7.** Kein Spam, Capslock oder wiederholte Nachrichten.\n"
                "**8.** Verkauf von Accounts, Daten oder Gegenständen ist verboten.\n\n"
                "❗ **Unwissenheit schützt nicht vor Strafe.**\n"
                "❗ **Strafen werden individuell vom Team vergeben.**\n"
                "❗ **Discord Richtlinien:** https://discord.com/new/guidelines\n\n"
                "**Klicke auf den Button unten, um dich zu verifizieren.**"
            ),
            color=discord.Color.blurple()
        )

        await channel.send(embed=embed, view=VerifyView())


async def setup(bot):
    await bot.add_cog(VerifyCog(bot))