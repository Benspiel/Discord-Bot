import os
import asyncio
import discord
from discord.ext import commands

# =========================
#   TOKEN EINTRAGEN
# =========================
TOKEN = ""


# =========================
#   Intents
# =========================
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
#   Events
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user} (ID: {bot.user.id})")

    try:
        await bot.tree.sync()
        print("✅ Slash Commands gesynct")
    except Exception as e:
        print("❌ Fehler beim Sync:", e)


# =========================
#   Cogs laden
# =========================
def module_path_from_file(path: str) -> str:
    rel = os.path.relpath(path, ".")
    rel = rel[:-3] if rel.endswith(".py") else rel
    return rel.replace(os.sep, ".")


async def load_cogs():
    for root, dirs, files in os.walk("./cogs"):
        for file in files:
            if file.endswith(".py"):
                mod = module_path_from_file(os.path.join(root, file))
                if mod.startswith("cogs"):
                    try:
                        await bot.load_extension(mod)
                        print(f"⚡ Geladen: {mod}")
                    except Exception as e:
                        print(f"❌ Fehler beim Laden: {mod} → {e}")


# =========================
#   Main
# =========================
async def main():
    await load_cogs()
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())