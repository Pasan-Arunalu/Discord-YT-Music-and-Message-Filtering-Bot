#messagefilter.py
from discord.ext import commands

class MessageFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        msg = message.content.lower()
        scam_keywords = ["steam giveaway", "steam gift card", "free nitro"]
        scam_links = ["discord.gift/", "discord.gg/", "bit.ly/", "tinyurl.com/", "steamcommunity.com/", ".ru", ".xyz", ".tk"]

        if any(word in msg for word in scam_keywords) or any(link in msg for link in scam_links):
            await message.delete()
            await message.channel.send(f"Potential scam link from {message.author.mention} was removed.")
            return

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(MessageFilter(bot))
