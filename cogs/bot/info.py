import discord
from discord.ext import commands

INFO_CHANNEL = 1439619727902249011
TICKET_PANEL_CHANNEL = 1439619315409227787


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(INFO_CHANNEL)
        if not channel:
            return

        # Channel leeren
        try:
            await channel.purge(limit=20)
        except:
            pass

        # ---------- EMBED 1 – Willkommen ----------
        embed1 = discord.Embed(
            title="👋 Willkommen auf unserem Server!",
            description=(
                "Hier findest du eine kurze Übersicht über unser Ticketsystem,\n"
                "damit du weißt, wie du Hilfe bekommst oder Bewerbungen abschickst."
            ),
            color=discord.Color.blurple()
        )
        embed1.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")

        # ---------- EMBED 2 – Ticketsystem ----------
        embed2 = discord.Embed(
            title="🎫 Ticketsystem – Übersicht",
            description=(
                "Du kannst Tickets über einen einfachen Menü-Auswahl erstellen.\n\n"
                "📩 **Normales Ticket** – Allgemeine Fragen oder Anliegen\n"
                "🛠️ **Technischer Support** – Hilfe bei technischen Problemen\n"
                "📄 **Bewerbung** – Bewirb dich beim Server-Team\n\n"
                f"👉 Tickets erstellst du hier: <#{TICKET_PANEL_CHANNEL}>"
            ),
            color=discord.Color.green()
        )

        # ---------- EMBED 3 – Kategorien ----------
        embed3 = discord.Embed(
            title="📂 Ticket-Kategorien",
            description=(
                "Alle Tickets werden automatisch in den richtigen Kategorien erstellt:\n\n"
                "• **General** – Normale Tickets\n"
                "• **Tech Support** – Technische Probleme\n"
                "• **Bewerbung** – Bewerbungen fürs Team\n\n"
                "Die Kategorien helfen dem Team dabei, schneller zu reagieren."
            ),
            color=discord.Color.orange()
        )

        # ---------- EMBED 4 – Regeln ----------
        embed4 = discord.Embed(
            title="📌 Regeln fürs Ticketsystem",
            description=(
                "Bitte beachte folgende Hinweise, wenn du ein Ticket erstellst:\n\n"
                "• Schreibe klar und freundlich\n"
                "• Beschreibe dein Problem möglichst genau\n"
                "• Schreibe nicht mehrfach das gleiche Ticket\n"
                "• Beleidigungen oder Spam werden gelöscht\n"
                "• Gedulde dich — das Team antwortet so schnell wie möglich\n"
            ),
            color=discord.Color.red()
        )

        # ---------- EMBED 5 – Extras ----------
        embed5 = discord.Embed(
            title="ℹ️ Weitere Infos",
            description=(
                "• Tickets können jederzeit mit einem Button geschlossen werden\n"
                "• Das Team wird automatisch benachrichtigt, wenn du ein Ticket erstellst\n"
                "• Du wirst benachrichtigt, sobald das Team antwortet\n\n"
                "Viel Spaß auf unserem Server! ❤️"
            ),
            color=discord.Color.gold()
        )

        # Embeds senden
        await channel.send(embed=embed1)
        await channel.send(embed=embed2)
        await channel.send(embed=embed3)
        await channel.send(embed=embed4)
        await channel.send(embed=embed5)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))