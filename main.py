import logging

import discord
from discord.ext import commands
from discord.ext.commands import is_owner
import datetime
import matching
import roles
import audit
import voice
import pin

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8',
                                   mode='w')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(file_handler)
intents = discord.Intents(messages=True, guilds=True, reactions=True,
                          members=True, message_content=True)
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True,
                   help_command=None,
                   allowed_mentions=discord.AllowedMentions(everyone=False))


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    print('Time: {0}'.format(datetime.datetime.now(datetime.timezone.utc)))
    await bot.add_cog(matching.Matching(bot))
    await bot.add_cog(roles.Roles(bot))
    await bot.add_cog(audit.Audit(bot))
    await bot.add_cog(voice.Voice(bot))
    await bot.add_cog(pin.Pin(bot))


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
@is_owner()
async def msg(ctx, channel: int, *, text: str):
    await bot.get_channel(channel).send(text)


@bot.command()
@is_owner()
async def delete_category(ctx):
    if ctx.channel.category:
        await voice.delete_category_fully(ctx.channel.category)


@bot.command()
@is_owner()
async def mass_ban(ctx, *, text: str):
    lines = text.splitlines()
    for line in lines:
        try:
            user_id = int(line.split()[0][3:-1])
            member = ctx.guild.get_member(user_id)
            if member:
                await ctx.guild.ban(member, reason='spam bot')
                print('banned: ', member)
        except ValueError:
            print('ValueError: ', line.split()[0])


bot.allowed_mentions = discord.AllowedMentions(everyone=False)
bot.run('<BOT KEY HERE>')
