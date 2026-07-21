import os
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from database import init_db

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print (f"Loaded cog: {filename}")

@bot.event
async def on_ready():
    await init_db()
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")


async def main ():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)

import asyncio
asyncio.run(main())