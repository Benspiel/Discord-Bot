import discord
from discord.ext import commands, tasks
import aiohttp

# Repository
REPO = "Benspiel/Discord-Bot"
CHANNEL_ID = 1443692452249600221


class GitHubWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_commit = None
        self.check_commits.start()

    def cog_unload(self):
        self.check_commits.cancel()

    @tasks.loop(seconds=30)
    async def check_commits(self):
        await self.bot.wait_until_ready()

        url = f"https://api.github.com/repos/{REPO}/commits"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return
                data = await resp.json()

        if not data:
            return

        latest = data[0]  # neuester Commit
        sha = latest["sha"]

        # Beim ersten Start nur merken, nicht posten
        if self.last_commit is None:
            self.last_commit = sha
            return

        # Bereits bekannt?
        if sha == self.last_commit:
            return

        # neuen Commit merken
        self.last_commit = sha

        # GitHub Daten
        commit_info = latest["commit"]
        commit_msg = commit_info["message"]
        commit_author = commit_info["author"]["name"]
        commit_timestamp = commit_info["author"]["date"]
        commit_url = latest["html_url"]

        # Author Profilbild (wenn verfügbar)
        author_info = latest.get("author", None)
        avatar_url = author_info["avatar_url"] if author_info else None

        # Projektname
        repo_name = REPO.split("/")[-1]

        # === EMBED ===
        embed = discord.Embed(
            title=f"📦 Neues Update in *{repo_name}*",
            description=f"**{commit_author}** hat einen neuen Commit erstellt.",
            color=discord.Color.blurple(),
            timestamp=discord.utils.parse_time(commit_timestamp)
        )

        embed.add_field(
            name="💬 Commit Message",
            value=f"```{commit_msg}```",
            inline=False
        )

        embed.add_field(
            name="🔗 GitHub Link",
            value=f"[➡️ Zum Commit]({commit_url})",
            inline=True
        )

        embed.set_thumbnail(
            url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )

        # Author Avatar
        if avatar_url:
            embed.set_author(name=commit_author, icon_url=avatar_url)

        embed.set_footer(text="GitHub • Automatisches Repo Monitoring")

        # Senden
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

    @check_commits.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(GitHubWatcher(bot))
#