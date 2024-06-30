import asyncio

import aiohttp
import discord
from discord.ext import commands
import datetime
import time_parser
import files
import voice

small_timedelta = datetime.timedelta(minutes=15)
far_past = datetime.datetime(year=2000, month=4, day=4)
mentions = discord.AllowedMentions(everyone=False)

bot_user_id = 746401093508006000
guild_id = 624609341886169117

custom_emojis_to_add = [
    1257076567700668547,  # spice
    1257076627142213642,  # worthless
]
common_emojis_to_add = [
    '✍️',
    '❌',
]

edit_date_aliases = ["date", "time", "editdate", "edittime", "edit_time"]
edit_text_aliases = ["text", "title", "description", "edittext",
                     "edittitle", "editdescription", "edit_title",
                     "edit_description"]

play = 0
maybe = 1
delete = 2
edit = 3
emojis = {
    'spice': play,
    'imperium': play,
    'worthless': maybe,
    '❌': delete,
    '✍️': edit,
    'Lozenge': play,
    'Traitor': maybe,
    'Battle': delete,
    '🍺': play,
    '✅': play,
    '❓': maybe,
    'Season': play,
    'Triskele': maybe,
    'Geis': delete,
}

channels = {
    # lfg:              matches
    625131638887546890: 995753350408716308,    # classic dune
    900857355242184734: 995761430152368240,    # dune: conquest
    801911401156968478: 995752955464650782,    # dune: imperium
    1022775514278142002: 1022775384992911410,  # dune: war for arrakis
    744191730097586236: 995751425390936124,    # dune off-topic
    746433956894867506: 694601128402485258,    # test 1
    746433606259572899: 746433914595311688,    # test 2
    782783616232194068: 783402464493174816,    # eclipse
    778682723665051698: 778682593499414579,    # chaos in the old world
    833984225824866336: 833984400257056769,    # inis
    822605513623339008: 855472640847773696,    # dune play-testing
    1032408375507566612: 1032672765070811218,  # dune: imperium ranked
    1257052124597194913: 1257052081802448937,  # public test
}
channels_reverse = {}
for k, v in channels.items():
    channels_reverse[v] = k

matches = {}


async def update_timer():
    while True:
        await asyncio.sleep(delay=300)
        for match_id, match in matches.copy().items():
            try:
                await match.update()
                # print("match updated")
            except discord.errors.NotFound:
                print("Error: did not find match ", match_id)
                files.delete(match_id=match_id)
                if match_id in matches:
                    del matches[match_id]
            except discord.errors.DiscordServerError:
                print("Error: timed update DiscordServerError", match_id)
            except asyncio.TimeoutError:
                print("Error: timed update timed out")
            except KeyError:
                print("Error: timed update KeyError")
            except aiohttp.ClientConnectorError:
                print("Error: timed update ClientConnectorError")
            except aiohttp.ClientOSError:
                print("Error: timed update ClientOSError")
            except discord.errors.HTTPException:
                await asyncio.sleep(delay=60)
                print("Error: timed update HTTPException")
            except discord.ext.commands.errors.MissingRequiredArgument:
                print("Error: timed update MissingRequiredArgument")
            except aiohttp.ServerDisconnectedError:
                await asyncio.sleep(delay=60)
                print("Error: timed update ServerDisconnectedError")


class Match:
    def __init__(self, bot, channel, host, time, note, players=None,
                 maybes=None, msg_id=None, creation_msg=None,
                 creation_msg_id=None, invites_sent=False):
        self.bot = bot
        self.channel = channel
        self.host = host
        if time is None:
            self.asap = True
            self.time = datetime.datetime.now(datetime.timezone.utc).replace(
                second=0, microsecond=0)
        else:
            self.asap = False
            self.time = time
        self.note = note
        self.players = players
        self.maybes = maybes
        self.message = None
        self.msg_id = msg_id
        self.creation_msg = creation_msg
        self.creation_msg_id = creation_msg_id
        self.invites_sent = invites_sent
        if not players:
            self.players = [host]
        if not maybes:
            self.maybes = []
        self.embed = discord.Embed(color=discord.Color.green())

    def get_host(self):
        return self.host

    def edit_time(self, text):
        parser = time_parser.TimeParser(raw=text)
        time = parser.get_time()
        if time is None:
            self.asap = True
            self.time = datetime.datetime.now(datetime.timezone.utc).replace(
                second=0, microsecond=0)
        else:
            self.asap = False
            self.time = time
        self.invites_sent = False

    def edit_note(self, text):
        self.note = text

    def set_message(self, message):
        self.message = message

    def set_msg_id(self, msg_id):
        self.msg_id = msg_id

    def add_player(self, user):
        if user not in self.players:
            self.players.append(user)

    def add_maybe(self, user):
        if user not in self.maybes:
            self.maybes.append(user)

    def remove_player(self, user):
        if user in self.players:
            self.players.remove(user)

    def remove_maybe(self, user):
        if user in self.maybes:
            self.maybes.remove(user)

    def mark_delete(self):
        self.time = far_past

    def save(self):
        data = {
            'channel': self.channel,
            'host': self.host,
            'time': self.time,
            'note': self.note,
            'players': self.players,
            'maybes': self.maybes,
            'creation_msg_id': self.creation_msg_id,
            'invites_sent': self.invites_sent,
        }
        files.save(match_id=self.message.id, match_data=data)

    async def update(self):
        if not self.message:
            self.message = await self.bot.get_channel(
                self.channel).fetch_message(self.msg_id)
        if not self.creation_msg:
            self.creation_msg = await self.bot.get_channel(
                channels_reverse[self.channel]).fetch_message(
                self.creation_msg_id)
        now = datetime.datetime.now(self.time.tzinfo).replace(second=0,
                                                              microsecond=0)
        if now - self.time > datetime.timedelta(hours=12):
            print('deleting: {0}'.format(self.message.id))
            del matches[self.message.id]
            files.delete(match_id=self.message.id)
            await self.message.delete()
            return

        self.embed.clear_fields()

        # for i in range(len(self.players)):
        #     self.embed.add_field(name=str(i + 1) + '. ', inline=True,
        #                          value=self.bot.get_user(
        #                              self.players[i]).mention)

        if len(self.players) != 0:
            players_text = ''
            for i in range(len(self.players)):
                players_text += str(i + 1) + '. '
                players_text += self.bot.get_user(
                    self.players[i]).mention
                players_text += ' ||' + self.bot.get_user(
                    self.players[i]).display_name + '||\n'
            self.embed.add_field(name='Players', value=players_text,
                                 inline=False)
        if len(self.maybes) != 0:
            maybe_text = ''
            for i in range(len(self.maybes)):
                maybe_text += self.bot.get_user(self.maybes[i]).mention
                maybe_text += ' ||' + self.bot.get_user(
                    self.maybes[i]).display_name + '||\n'
            self.embed.add_field(name='Maybes', value=maybe_text, inline=False)

        if self.asap:
            self.embed.add_field(name='Time: As Soon As Possible',
                                 value='Uptime: ' + str(-(self.time - now)),
                                 inline=False)
        elif (self.time - now) < datetime.timedelta(0):
            self.embed.add_field(name='MATCH STARTED',
                                 value='Uptime: ' + str(-(self.time - now)),
                                 inline=False)
        else:
            self.embed.add_field(name='ETA', value=str(self.time - now),
                                 inline=False)

        emojis_in_embed = []
        for emoji_id in custom_emojis_to_add:
            emojis_in_embed.append(self.bot.get_emoji(emoji_id))
        emoji_explanation = f'{emojis_in_embed[0]} Yes {emojis_in_embed[1]} ' \
                            f'Maybe ✍️ Edit ❌ Delete'
        self.embed.add_field(name='Emoji Reactions', value=emoji_explanation,
                             inline=False)

        self.embed.title = self.bot.get_user(self.host).name + "'s Match"
        self.embed.description = self.note
        self.embed.timestamp = self.time
        self.embed.url = self.creation_msg.jump_url

        if not self.invites_sent and (self.time - now) < small_timedelta:
            self.invites_sent = True
            host_user = self.bot.get_user(self.host)
            invite = await voice.make_channels(bot=self.bot, author=host_user,
                                               guild=self.message.guild,
                                               extra_channels=1)
            invite_text = self.embed.title
            invite_text += " is starting soon!\n"
            invite_text += "This voice channel will be used:\n"
            invite_text += invite.url
            await self.creation_msg.channel.send(invite_text)
            for user_id in self.players:
                user = self.bot.get_user(user_id)
                try:
                    await user.send(invite_text)
                except discord.errors.Forbidden:
                    print('inviting {0} was forbidden'.format(user.name))
            host_instructions = "If you would like to add extra voice " \
                                "channels to your match, use the !extra " \
                                "command anywhere. For example, sending " \
                                "!extra 3 adds 3 extra voice channels.\n" \
                                "If your match is done and you would like " \
                                "to delete the channels, use the !finish " \
                                "command anywhere. Channels will " \
                                "automatically be deleted 12 hours after " \
                                "their creation."
            try:
                await host_user.send(host_instructions)
            except discord.errors.Forbidden:
                print('inviting {0} was forbidden'.format(user.name))

        self.save()
        try:
            await self.message.edit(embed=self.embed,
                                    allowed_mentions=mentions)
        except aiohttp.ClientOSError:
            print("Error: match update ClientOSError")


class Matching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(guild_id)
        for k, v in files.get_matches().items():
            matches[k] = Match(bot=self.bot, channel=v['channel'], host=v[
                'host'], time=v['time'], note=v['note'], players=v[
                'players'], maybes=v['maybes'], msg_id=k, creation_msg_id=v[
                'creation_msg_id'], invites_sent=v['invites_sent'])
        asyncio.ensure_future(update_timer())

    @commands.command()
    async def help(self, ctx, arg=''):
        if ctx.channel.id in channels:
            await ctx.channel.send(files.get_help(arg),
                                   allowed_mentions=mentions)

    @commands.command(aliases=['new'])
    async def lfg(self, ctx, *, text):
        print(f'!lfg {text}')
        print(f'creation_msg: {ctx.message.jump_url}')
        if ctx.channel.id in channels:
            parser = time_parser.TimeParser(raw=text)
            time = parser.get_time()
            match = Match(bot=self.bot, channel=channels[ctx.channel.id],
                          host=ctx.author.id, time=time, note=text,
                          creation_msg=ctx.message,
                          creation_msg_id=ctx.message.id)
            embed = discord.Embed(color=discord.Color.dark_gray(),
                                  description="Generating", title="Generating")
            match.set_message(await self.bot.get_channel(match.channel).send(
                embed=embed, allowed_mentions=mentions))
            matches[match.message.id] = match
            match.save()
            for emoji_id in custom_emojis_to_add:
                emoji = await self.guild.fetch_emoji(emoji_id)
                await match.message.add_reaction(emoji)
            for emoji_str in common_emojis_to_add:
                await match.message.add_reaction(emoji_str)
            await match.update()

    @commands.command(aliases=['remove'])
    async def delete(self, ctx):
        for match in matches.values():
            if match.host == ctx.author.id:
                match_to_delete = match
        match_to_delete.mark_delete()

    @commands.command()
    async def edit(self, ctx, *, text):
        for match in matches.values():
            if match.host == ctx.author.id:
                match_to_edit = match
        match_to_edit.edit_time(text)
        match_to_edit.edit_note(text)
        await match.update()

    @commands.command(aliases=edit_date_aliases)
    async def edit_date(self, ctx, *, text):
        for match in matches.values():
            if match.host == ctx.author.id:
                match_to_edit = match
        match_to_edit.edit_time(text)
        await match.update()

    @commands.command(aliases=edit_text_aliases)
    async def edit_text(self, ctx, *, text):
        for match in matches.values():
            if match.host == ctx.author.id:
                match_to_edit = match
        match_to_edit.edit_note(text)
        await match.update()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji.name
        user_id = payload.user_id
        msg_id = payload.message_id
        if msg_id in matches and emoji in emojis and user_id != bot_user_id:
            match = matches[msg_id]
            if emojis[emoji] == play:
                match.add_player(user_id)
                await match.update()
            elif emojis[emoji] == maybe:
                match.add_maybe(user_id)
                await match.update()
            elif emojis[emoji] == delete:
                if user_id == match.get_host():
                    print('mark delete: {0}'.format(msg_id))
                    match.mark_delete()
                else:
                    error_message = "You cannot delete this match because " \
                                    "you are not its creator!"
                    await self.bot.get_user(user_id).send(error_message)
            elif emojis[emoji] == edit:
                if user_id == match.get_host():
                    message = "✍️Edit your most recent match with !text, " \
                              "!time, or !edit. For example:\n"
                    message += "!text Vanilla Advanced -> match text " \
                               "becomes 'Vanilla Advanced'\n"
                    message += "!time tomorrow, 10pm UTC+1 -> match time " \
                               "becomes tomorrow, 10pm UTC+1\n"
                    message += "!edit tomorrow, 10pm UTC+1 ! Vanilla " \
                               "Advanced -> match time becomes tomorrow, " \
                               "10pm UTC+1 and match text becomes 'tomorrow," \
                               " 10pm UTC+1 ! Vanilla Advanced'"
                else:
                    message = "You cannot edit this match because " \
                              "you are not its creator!"
                await self.bot.get_user(user_id).send(message)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        emoji = payload.emoji.name
        user_id = payload.user_id
        msg_id = payload.message_id
        if msg_id in matches and emoji in emojis:
            match = matches[msg_id]
            if emojis[emoji] == play:
                match.remove_player(user_id)
                await match.update()
            elif emojis[emoji] == maybe:
                match.remove_maybe(user_id)
                await match.update()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        msg_id = payload.message_id
        if msg_id in matches:
            matches[msg_id].mark_delete()
