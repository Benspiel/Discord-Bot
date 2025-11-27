import discord
from discord.ext import commands

CHANNEL_ID = 1443699258778714152

class ToDo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ============================
    #   MESSAGE HANDLER
    # ============================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != CHANNEL_ID:
            return

        content = message.content
        try:
            await message.delete()
        except:
            pass

        embed = discord.Embed(
            title="📌 Neues To-Do",
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(
            text=f"Eingereicht von {message.author}",
            icon_url=message.author.display_avatar.url
        )

        todo = await message.channel.send(embed=embed)

        # Standard-Reaktionen hinzufügen
        await todo.add_reaction("✅")
        await todo.add_reaction("❌")
        await todo.add_reaction("⏳")

    # ============================
    #   REACTION HANDLER
    # ============================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Bot eigene Reaktionen ignorieren
        if payload.user_id == self.bot.user.id:
            return

        if payload.channel_id != CHANNEL_ID:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = str(payload.emoji)

        # Nur To-Do Embeds bearbeiten
        if not message.embeds:
            return

        embed = message.embeds[0]

        # ============================
        #   HAKEN → GRÜN + andere weg
        # ============================
        if emoji == "✅":
            new_embed = embed.copy()
            new_embed.color = discord.Color.green()

            await message.edit(embed=new_embed)

            # Andere Reaktionen löschen
            for r in message.reactions:
                if str(r.emoji) != "✅":
                    await message.clear_reaction(r.emoji)

        # ============================
        #   ABGELEHNT → ROT + andere weg
        # ============================
        elif emoji == "❌":
            new_embed = embed.copy()
            new_embed.color = discord.Color.red()

            await message.edit(embed=new_embed)

            for r in message.reactions:
                if str(r.emoji) != "❌":
                    await message.clear_reaction(r.emoji)

        # ============================
        #   ARBEITE DRAN → GELB
        # ============================
        elif emoji == "⏳":
            new_embed = embed.copy()
            new_embed.color = discord.Color.gold()

            await message.edit(embed=new_embed)
            # NICHT entfernen → soll bleiben


async def setup(bot):
    await bot.add_cog(ToDo(bot))
