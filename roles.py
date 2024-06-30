import discord
from discord.ext import commands
from discord.ext.commands import is_owner

guild_id = 624609341886169117

role_dict = {
    # temp
    0: {
        'spice': 'Dune',
        'imperium': 'Dune: Imperium',
        'treachery': 'Modding',
        'alliance': 'Off-Topic',
        'truth': 'Dune Spoilers',
    },
    # Channel Access Roles
    894281184882864138: {
        'truth': 'Dune Spoilers',
    },
    # Color/Faction Roles
    801945810815549471: {
        'atr': 'Atreides',
        'bg': 'Bene Gesserit',
        'emp': 'Emperor',
        'frem': 'Fremen',
        'guild': 'Spacing Guild',
        'hark': 'Harkonnen',
        'ix': 'Ixian',
        'bt': 'Tleilaxu',
        'choam': 'CHOAM',
        'richese': 'Richese',
        'ecaz': 'Ecaz',
        'moritani': 'Moritani',
    },
    # LFG Roles
    # Dune Board Game
    801945812862500914: {
        'basic': 'LFG Basic',
        'advanced': 'LFG Advanced',
        'wormtoken': 'LFG Vanilla',
        'expansion': 'LFG Expansion 1',
        'ch': 'LFG Beginner',
        'exp2': 'LFG Expansion 2',
        'Shrine': 'LFG Expansion 3',
    },
    # Other
    801945814234562600: {
        '🎲': 'LFG Non-Dune',
        'imperium': 'LFG Imperium',
        '🧠': 'LFG Dune TTRPG',
        'conquest': 'LFG Conquest',
        'worm_war': 'LFG War for Arrakis',
    },
    # Custom
    801945815378558977: {
        '🌈': 'LFG Dreamer',
        '🌏': 'LFG Asia/Oceania',
        'treachery': 'LFG Treachery Online',
    },
    # Tourney
    834116714101997599: {
        'sandworm': 'Tournament Participant',
    }
}


def get_role_name(msg_id, emoji):
    if msg_id in role_dict and emoji in role_dict[msg_id]:
        return role_dict[msg_id][emoji]
    else:
        return None


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(guild_id)

    @is_owner()
    @commands.command()
    async def add_channel_roles_to_all(self, ctx):
        if self.guild is None:
            self.guild = self.bot.get_guild(guild_id)
        roles = []
        for role_name in role_dict[0].values():
            roles.append(discord.utils.get(self.guild.roles, name=role_name))
        print(len(roles))
        countdown = len(self.guild.members)
        print(countdown)
        for member in self.guild.members:
            for role in roles:
                await member.add_roles(role)
            countdown -= 1
            print(countdown)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        msg_id = payload.message_id
        emoji = payload.emoji.name
        user_id = payload.user_id
        role_name = get_role_name(msg_id, emoji)
        if role_name:
            if self.guild is None:
                self.guild = self.bot.get_guild(guild_id)
            member = self.guild.get_member(user_id)
            role = discord.utils.get(self.guild.roles, name=role_name)
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        msg_id = payload.message_id
        emoji = payload.emoji.name
        user_id = payload.user_id
        role_name = get_role_name(msg_id, emoji)
        if role_name:
            if self.guild is None:
                self.guild = self.bot.get_guild(guild_id)
            member = self.guild.get_member(user_id)
            role = discord.utils.get(self.guild.roles, name=role_name)
            await member.remove_roles(role)
