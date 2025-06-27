# music.py
import os
import asyncio
from collections import deque
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks
import yt_dlp

CACHE_DURATION = timedelta(minutes=60)
song_cache: dict[str, tuple[str, datetime]] = {}

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, deque] = {}

        self.cleanup.start()

    def cog_unload(self):
        self.cleanup.cancel()

    @tasks.loop(minutes=10)
    async def cleanup(self):

        now = datetime.now()
        stale_ids = []

        for vid, (file_path, ts) in list(song_cache.items()):
            if now - ts > CACHE_DURATION:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"[CLEANUP] Removed '{file_path}'")
                except Exception as e:
                    print(f"[CLEANUP ERROR] Cannot remove '{file_path}': {e}")
                stale_ids.append(vid)

        for vid in stale_ids:
            song_cache.pop(vid, None)

    @commands.command()
    async def play(self, ctx: commands.Context, url: str | None = None):
        if not url:
            return await ctx.send("Provide a YouTube / YouTube-Music URL.")

        if not ctx.author.voice:
            return await ctx.send("Join a voice channel first!")

        voice_channel = ctx.author.voice.channel
        vc: discord.VoiceClient | None = ctx.voice_client

        if not vc or not vc.is_connected():
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

        os.makedirs("music", exist_ok=True)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "music/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "ffmpeg_location": "/usr/bin/ffmpeg",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info["id"]
            title = info["title"]
            filename = (
                ydl.prepare_filename(info)
                .replace(".webm", ".mp3")
                .replace(".m4a", ".mp3")
            )

            now = datetime.now()
            if video_id in song_cache and now - song_cache[video_id][1] < CACHE_DURATION:
                print("[CACHE] Using cached file")
            else:
                print("[DOWNLOAD] Downloading new audio")
                ydl.download([url])
                print(f"[FILE CHECK] Exists? {os.path.exists(filename)} - {filename}")
                song_cache[video_id] = (filename, now)

        guild_id = ctx.guild.id
        self.queues.setdefault(guild_id, deque()).append((filename, title, ctx))

        if not vc.is_playing() and not vc.is_paused():
            await self._play_next(vc, guild_id)
        else:
            await ctx.send(f"Added to queue: **{title}**")

    async def _play_next(self, vc: discord.VoiceClient, guild_id: int):
        if guild_id not in self.queues or not self.queues[guild_id]:
            await vc.disconnect()
            return

        filename, title, ctx = self.queues[guild_id].popleft()

        def _after_playing(error):
            if error:
                print(f"[FFmpeg error] {error}")
            fut = asyncio.run_coroutine_threadsafe(
                self._play_next(vc, guild_id), self.bot.loop
            )
            try:
                fut.result()
            except Exception as exc:
                print(f"[ERROR] after_playing: {exc}")

        ffmpeg_path = "/usr/bin/ffmpeg"
        print(f"[PLAY] Playing file: {filename}")
        vc.play(
            discord.FFmpegPCMAudio(source=filename, executable=ffmpeg_path),
            after=_after_playing,
        )
        print("[PLAY] Sent to VC")
        await ctx.send(
            f"▶ **{title}**\nRequested by {ctx.author.mention}"
        )

    @commands.command()
    async def queue(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        q = self.queues.get(guild_id, deque())
        if not q:
            return await ctx.send("Queue is empty.")
        msg_lines = [f"{idx+1}. {item[1]}" for idx, item in enumerate(q)]
        await ctx.send("**Current queue:**\n" + "\n".join(msg_lines))

    @commands.command()
    async def skip(self, ctx: commands.Context):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏭ Skipped.")
        else:
            await ctx.send("Nothing is playing.")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        self.queues.pop(guild_id, None)  # clear queue
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
        await ctx.send("⏹ Stopped and left the voice channel.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and before.channel and not after.channel:
            guild_id = before.channel.guild.id
            self.queues.pop(guild_id, None)

    @commands.command()
    async def ping(self, ctx):
      await ctx.send("Pong!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
