from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import is_owner

mentions = discord.AllowedMentions(everyone=False)

guild_id = 624609341886169117

channels = {
    "msg_log": 884891060558504006,
}


class Audit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.guild_id == guild_id:
            channel = self.bot.get_channel(payload.channel_id).name

            embed = discord.Embed(color=discord.Color.red())
            embed.title = "Message deleted from #" + channel

            msg = payload.cached_message
            if msg is not None and not msg.author.bot:
                embed.description = msg.content + "\n--" + msg.author.name

            await self.bot.get_channel(channels["msg_log"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if payload.guild_id == guild_id:
            channel = self.bot.get_channel(payload.channel_id).name

            embed = discord.Embed(color=discord.Color.gold())
            embed.title = "Message edited in #" + channel

            msg = payload.cached_message
            if msg is not None and not msg.author.bot:
                embed.description = msg.content + "\n--" + msg.author.name
                embed.url = msg.jump_url
                await self.bot.get_channel(channels["msg_log"]).send(
                    embed=embed)
