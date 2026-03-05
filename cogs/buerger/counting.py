import discord
from discord.ext import commands

class CountGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Deine Channel ID
        self.channel_id = 1439619613729230939

        self.last_number = 0
        self.last_user = None

        self.ok_emoji = "✅"
        self.fail_emoji = "❌"

    @commands.Cog.listener()
    async def on_ready(self):
        """Scannt beim Bot-Start die letzte gültige Zahl."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        async for msg in channel.history(limit=200, oldest_first=False):
            if msg.author.bot:
                continue
            # Nur Nachrichten werten, die eine reine Zahl sind
            if msg.content.strip().isdigit():
                self.last_number = int(msg.content.strip())
                self.last_user = msg.author.id
                return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != self.channel_id:
            return

        content = message.content.strip()

        # ÄNDERUNG: Wenn es keine Zahl ist, ignorieren wir die Nachricht komplett
        if not content.isdigit():
            return

        number = int(content)

        # Prüfen, ob derselbe User zweimal hintereinander schreibt
        if message.author.id == self.last_user:
            await self.user_twice(message)
            return

        # Prüfen, ob die Zahl die richtige Reihenfolge hat
        if number != self.last_number + 1:
            await self.wrong_number(message)
            return

        # Alles korrekt!
        self.last_number = number
        self.last_user = message.author.id

        try:
            await message.add_reaction(self.ok_emoji)
        except:
            pass

    async def wrong_number(self, message: discord.Message):
        """Falsche Zahl -> ❌ Reaction, Reset auf 0."""
        try:
            await message.add_reaction(self.fail_emoji)
        except:
            pass

        await message.channel.send(
            f"❌ {message.author.mention} hat die falsche Zahl geschrieben – es geht wieder bei **0** los!"
        )

        self.last_number = 0
        self.last_user = None

    async def user_twice(self, message: discord.Message):
        """User schreibt zweimal hintereinander -> Nachricht löschen & DM."""
        try:
            await message.delete()
        except:
            pass

        embed = discord.Embed(
            title="❌ Du darfst nicht zweimal hintereinander zählen!",
            description="Bitte warte, bis jemand anderes dran ist.",
            color=discord.Color.red()
        )
        embed.add_field(name="Deine Nachricht:", value=f"```{message.content}```", inline=False)

        try:
            await message.author.send(embed=embed)
        except:
            pass

async def setup(bot):
    await bot.add_cog(CountGame(bot))