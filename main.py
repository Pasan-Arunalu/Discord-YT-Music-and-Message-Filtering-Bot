# main.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
import logging
import asyncio

# ── Load .env that lives next to this script ───────────────────────────
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
token = os.getenv("DISCORD_TOKEN")

# Debug - remove these two lines after it works
print(f"[DEBUG] .env found at {env_path}: {env_path.exists()}")
print(f"[DEBUG] Token loaded? {token is not None}")

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Bot is ready.')

# async setup function to load extensions
async def setup():
    await bot.load_extension("music")
    await bot.load_extension("messagefilter")
    await bot.start(token)

# run the bot properly
if __name__ == '__main__':
    asyncio.run(setup())
