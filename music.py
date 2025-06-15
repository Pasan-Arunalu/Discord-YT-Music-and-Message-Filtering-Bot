# music.py
import os
import discord
import asyncio
from discord.ext import commands
import yt_dlp

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
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')

            ffmpeg_path = r"C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
            vc.play(discord.FFmpegPCMAudio(source=filename, executable=ffmpeg_path))
            await ctx.send(f"Now playing: **{info['title']}**")

        except Exception as e:
            print(f"[ERROR in Play] {e}]")
            await ctx.send(f"Failed to play: `{str(e)}`")

        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Stopped and left the Voice Channel!")

async def setup(bot):
    await bot.add_cog(Music(bot))