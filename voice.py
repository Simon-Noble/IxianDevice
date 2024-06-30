import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands

update_delay_minutes = 30
max_age_hours = 12
max_timedelta = timedelta(hours=max_age_hours)

max_extra_channels = 16
bitrate = 64000

text_category_id = 962688194791505950


async def delete_expired_channels(bot):
    text_category = bot.get_channel(text_category_id)
    while True:
        for text_channel in text_category.channels:
            if (datetime.utcnow() - text_channel.created_at.replace(tzinfo=None)) > max_timedelta:
                voice_category_id = int(text_channel.topic.split()[1])
                voice_category = bot.get_channel(voice_category_id)
                await delete_category_fully(voice_category)
                await text_channel.delete()
        await asyncio.sleep(delay=update_delay_minutes * 60)


async def make_channels(bot, author, guild, extra_channels=1):
    max_age_seconds = max_age_hours * 60 * 60
    print("making {0}'s channels".format(author.name))

    text_category = bot.get_channel(text_category_id)
    text_channel_name = author.name + "-ingame"

    for text_channel in text_category.channels:
        topic = text_channel.topic
        match_data = topic.split()
        host_id = int(match_data[0])
        voice_category_id = int(match_data[1])
        if host_id == author.id:
            await text_channel.delete()
            await text_category.create_text_channel(text_channel_name,
                                                    topic=topic)
            main_channel = bot.get_channel(voice_category_id).channels[0]
            return await main_channel.create_invite(max_age=max_age_seconds)

    voice_category = await guild.create_category(
        author.name + "'s Match", position=len(guild.categories))
    topic = str(author.id) + " " + str(voice_category.id)
    await text_category.create_text_channel(text_channel_name, topic=topic)
    main_channel = await voice_category.create_voice_channel(
        author.name + " A", bitrate=bitrate)
    for i in range(max(min(extra_channels, max_extra_channels), 0)):
        await voice_category.create_voice_channel(
            author.name + " " + chr(ord('B') + i), bitrate=bitrate)
    # returns invite to main voice channel
    return await main_channel.create_invite(max_age=max_age_seconds)


async def delete_category_fully(category):
    if not category:
        print("could not delete category: Nullpointer")
        return
    try:
        category_name = category.name
        print("deleting category: {0}".format(category_name))
    except discord.errors.NotFound:
        print("did not find category with unknown name")
        return
    for channel in category.channels:
        try:
            await channel.delete()
        except discord.errors.NotFound:
            print("did not find channel")
    try:
        await category.delete()
    except discord.errors.NotFound:
        print("did not find category: {0}".format(category_name))


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        asyncio.ensure_future(delete_expired_channels(bot))

    @commands.command()
    async def voice(self, ctx, arg=0):
        invite = await make_channels(self.bot, author=ctx.author,
                                     guild=ctx.guild, extra_channels=arg)
        await ctx.send(invite)

    @commands.command()
    async def extra(self, ctx, arg=1):
        text_category = self.bot.get_channel(text_category_id)

        for text_channel in text_category.channels:
            match_data = text_channel.topic.split()
            host_id = int(match_data[0])
            voice_category_id = int(match_data[1])

            if host_id == ctx.author.id:
                voice_category = self.bot.get_channel(voice_category_id)
                extra_start = len(voice_category.channels) - 2
                extra_end = min(extra_start + arg, max_extra_channels)
                for i in range(extra_start, extra_end):
                    await voice_category.create_voice_channel(
                        ctx.author.name + " " + chr(ord('B') + i),
                        bitrate=bitrate)

    @commands.command()
    async def finish(self, ctx):
        text_category = self.bot.get_channel(text_category_id)
        for text_channel in text_category.channels:
            match_data = text_channel.topic.split()
            host_id = int(match_data[0])
            voice_category_id = int(match_data[1])
            if host_id == ctx.author.id:
                voice_category = self.bot.get_channel(voice_category_id)
                await delete_category_fully(voice_category)
                await text_channel.delete()
