# music.py
import os
import discord
import asyncio
from discord.ext import commands
import yt_dlp
from datetime import datetime, timedelta

song_cache = {}
CACHE_DURATION = timedelta(minutes=60)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, url=None):
        if not url:
            return await ctx.send('Provide a YT/ YT Music URL!')

        if not ctx.author.voice:
            return await ctx.send('Connect to a voice channel first!')

        voice_channel = ctx.author.voice.channel
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

        await asyncio.sleep(1)

        try:
            if not vc:
                vc = await voice_channel.connect()

            os.makedirs('music', exist_ok=True)

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "music/%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "ffmpeg_location": "C:/ffmpeg-7.1.1-essentials_build/bin",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)  # Only extract info first
                video_id = info['id']
                title = info['title']
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

                now = datetime.now()
                if video_id in song_cache and now - song_cache[video_id][1] < CACHE_DURATION:
                    print("[CACHE] Using cached file")
                else:
                    print("[DOWNLOAD] Downloading audio")
                    ydl.download([url])
                    song_cache[video_id] = (filename, now)

            ffmpeg_path = r"C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
            vc.play(discord.FFmpegPCMAudio(source=filename, executable=ffmpeg_path))
            await ctx.send(f"Now playing: **{title}**\nRequested by: **{ctx.author.display_name}**")

        except Exception as e:
            print(f"[ERROR in Play] {e}")
            await ctx.send(f"Failed to play: `{str(e)}`")

        while vc.is_playing():
            if not vc.is_connected():
                print("[INFO] Bot was manually disconnected from voice channel.")
                break
            await asyncio.sleep(1)

        if vc.is_connected():
            await vc.disconnect()

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Stopped and left the Voice Channel!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after, ctx):
        # Check if the bot was disconnected from a voice channel
        if member == self.bot.user:
            if before.channel is not None and after.channel is None:
                await ctx.send("Bot was disconnected from the voice channel by a user!")
                print("[INFO] Bot was disconnected from a voice channel by user.")

async def setup(bot):
    await bot.add_cog(Music(bot))