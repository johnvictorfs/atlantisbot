# Standard lib imports
import time

# Non-Standard lib imports
import rs3clans as rs3
import discord
from discord.ext import commands

# Local imports
import definesettings as setting


class ClanCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['claninfo', 'clanexp', 'claexp', 'clainfo', 'clãexp', 'clãinfo', 'clan', 'cla'])
    async def clan_user_info(self, ctx, *, username):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'clan_user_exp'.")
        start_time = time.time()

        message = setting.MESSAGES["clan_messages"]
        player = rs3.Player(name=username)
        player.set_runemetrics_info()
        if not player.exists:
            await ctx.send(message["player_does_not_exist"][setting.LANGUAGE].format(player.name))
            return
        try:
            user_clan = rs3.Clan(name=player.clan)
        except rs3.ClanNotFoundError:
            await ctx.send(message["player_not_in_clan"][setting.LANGUAGE].format(player.name))
            return
        try:
            # Case insensitive dictionary search mock-up
            lower_clan_dict = {}
            for key in user_clan.member:
                lower_clan_dict[key.lower().replace("\xa0", " ")] = user_clan.member[key]
            lower_name = player.name.lower()
            user_clan_exp = lower_clan_dict[lower_name]['exp']
            user_rank = lower_clan_dict[lower_name]['rank']
        except KeyError:
            await ctx.send(message["player_not_in_clan"][setting.LANGUAGE].format(player.name))
            return
        display_username = player.name
        if setting.SHOW_TITLES:
            if player.suffix:
                display_username = f"{player.name} {player.title}"
            else:
                display_username = f"{player.title} {player.name}"

        user_url_name = player.name.replace(" ", "%20")
        user_url_clan = player.clan.replace(" ", "%20")
        icon_url = f"https://secure.runescape.com/m=avatar-rs/{user_url_name}/chat.png"
        runeclan_url = f"https://runeclan.com/player/{user_url_name}"
        clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{user_url_clan}/clanmotif.png"

        embed_title = "RuneClan"
        rank_header = "__Rank__"
        clan_header = message["clan_header"][setting.LANGUAGE]
        exp_header = message["exp_header"][setting.LANGUAGE]
        total_exp_header = message["total_exp_header"][setting.LANGUAGE]
        private_profile_header = message["private_profile_header"][setting.LANGUAGE]

        user_rank_f = setting.CLAN_SETTINGS[user_rank]
        rank_emoji = user_rank_f['Emoji']
        if setting.LANGUAGE == 'Portuguese':
            user_rank = user_rank_f['Translation']

        clan_info_embed = discord.Embed(title=embed_title,
                                        description="",
                                        color=discord.Colour.dark_blue(),
                                        url=runeclan_url,
                                        )

        clan_info_embed.set_author(icon_url=icon_url, name=display_username)
        clan_info_embed.set_thumbnail(url=clan_banner_url)
        clan_info_embed.add_field(name=clan_header, value=player.clan)
        clan_info_embed.add_field(name=rank_header, value=f"{user_rank} {rank_emoji}")
        clan_info_embed.add_field(name=exp_header, value=f"{user_clan_exp:,}")
        if player.private_profile:
            clan_info_embed.add_field(name=total_exp_header, value=private_profile_header)
        else:
            clan_info_embed.add_field(name=total_exp_header, value=f"{player.exp:,}")

        await ctx.send(content=None, embed=clan_info_embed)
        print(f"    - Answer sent. Took: {time.time() - start_time:.2f}s")

    @commands.command(aliases=['shit', 'stuff'])
    async def tests(self, ctx):
        print('tests')
        await ctx.send("Hello World")
        tags_channel = self.bot.get_channel(499405987585720320)
        async for message in tags_channel.history():
            await message.delete()

def setup(bot):
    bot.add_cog(ClanCommands(bot))
