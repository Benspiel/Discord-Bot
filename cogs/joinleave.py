import discord
from discord.ext import commands
from datetime import datetime

JOIN_CHANNEL_ID = 1439599372907057230     # Join Channel
LEAVE_CHANNEL_ID = 1439628281505644574    # Leave Channel


class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------ MEMBER JOINS ------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(JOIN_CHANNEL_ID)
        if channel is None:
            print("JOIN-Channel nicht gefunden!")
            return

        embed = discord.Embed(
            title="👋 Neues Mitglied",
            description=f"{member.mention} ist dem Server beigetreten!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"User ID: {member.id}")

        await channel.send(embed=embed)

    # ------------ MEMBER LEAVES ------------
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
        if channel is None:
            print("LEAVE-Channel nicht gefunden!")
            return

        embed = discord.Embed(
            title="👋 Mitglied hat den Server verlassen",
            description=f"**{member}** hat den Server verlassen.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"User ID: {member.id}")

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(JoinLeave(bot))