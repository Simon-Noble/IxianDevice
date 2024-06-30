import discord
from discord.ext import commands
from discord.ext.commands import is_owner

#guild_id = 687274221524484114  # test server
guild_id = 624609341886169117  # real server
jaycyrzak_id = 232613762224357377

emojis = ['📌', '📍']


class Pin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(guild_id)

    async def get_thread_message_if_thread_owner(self, payload):
        msg_id = payload.message_id
        emoji = payload.emoji.name
        user_id = payload.user_id
        thread_id = payload.channel_id
        if emoji in emojis:
            if self.guild is None:
                self.guild = self.bot.get_guild(guild_id)
            thread = self.guild.get_thread(thread_id)
            if thread and thread.owner_id == user_id:
                return await thread.fetch_message(msg_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message = await self.get_thread_message_if_thread_owner(payload)
        if message:
            await message.pin(reason=f'pin_reaction_add')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message = await self.get_thread_message_if_thread_owner(payload)
        if message:
            await message.unpin(reason=f'pin_reaction_remove')
