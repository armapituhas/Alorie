import discord 
from discord.ext import commands
from config import DISCORD_TOKEN
from database import init_db

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await init_db()
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")

bot.run(DISCORD_TOKEN)