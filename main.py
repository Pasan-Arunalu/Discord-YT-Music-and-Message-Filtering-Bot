# main.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import asyncio

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
