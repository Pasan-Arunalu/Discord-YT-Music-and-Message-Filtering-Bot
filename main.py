import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import asyncio
import yt_dlp
import os

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
    print('Ready to go!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower()

    scam_keywords = ["steam giveaway", "steam gift card", "free nitro"]
    scam_links = ["discord.gift/", "discord.gg/", "bit.ly/", "tinyurl.com/", "steamcommunity.com/", ".ru", ".xyz", ".tk"]

    if any(word in msg for word in scam_keywords) or any(link in msg for link in scam_links):
        await message.delete()
        await message.channel.send(f"🚨 Potential scam link from {message.author.mention} was removed.")
        return

    await bot.process_commands(message)


@bot.command()
async def play(ctx, url=None):
    print("[DEBUG] play command called")  # First debug point

    if not url:
        print("[DEBUG] No URL provided")
        return await ctx.send("❌ You must provide a YouTube URL!")

    if not ctx.author.voice:
        print("[DEBUG] Author not in a voice channel")
        return await ctx.send("❌ You must be in a voice channel!")

    voice_channel = ctx.author.voice.channel
    vc = ctx.voice_client

    try:
        if not vc:
            print("[DEBUG] Connecting to voice channel...")
            vc = await voice_channel.connect()

        os.makedirs("music", exist_ok=True)

        ffmpeg_path = r"C:\ffmpeg-7.1.1-essentials_build\bin"  # Replace with your actual path

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': False,
            'ffmpeg_location': ffmpeg_path,  # ✅ this line tells yt_dlp where to find ffmpeg/ffprobe
            'outtmpl': 'music/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        print("[DEBUG] Downloading audio with yt_dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')

        print(f"[DEBUG] Playing file: {filename}")

        ffmpeg_path = r"C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

        vc.play(discord.FFmpegPCMAudio(
            source=filename,
            executable=ffmpeg_path
        ))

        await ctx.send(f"🎶 Now playing: **{info['title']}**")

    except Exception as e:
        print(f"[ERROR in play] {e}")
        await ctx.send(f"⚠️ Failed to play song: `{str(e)}`")

    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped and left the VC.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)



















