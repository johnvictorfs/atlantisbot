# Standard lib imports
import time

# Non-Standard lib imports
import rs3clans
import discord
from discord.ext import commands

# Local imports
import definesettings as setting
from .utils import separator


class ClanCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['claninfo', 'clanexp', 'claexp', 'clainfo', 'clãexp', 'clãinfo', 'clan', 'cla'])
    async def clan_user_info(self, ctx, *, username):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'clan_user_info'.")
        start_time = time.time()

        message = setting.MESSAGES["clan_messages"]
        player = rs3clans.Player(name=username, runemetrics=True)
        if not player.exists:
            print(f"    - Answer sent. Took: {time.time() - start_time:.2f}s")
            return await ctx.send(message["player_does_not_exist"][setting.LANGUAGE].format(player.name))
        try:
            user_clan = rs3clans.Clan(name=player.clan)
        except rs3clans.ClanNotFoundError:
            return await ctx.send(message["player_not_in_clan"][setting.LANGUAGE].format(player.name))
            print(f"    - Answer sent. Took: {time.time() - start_time:.2f}s")
        member = user_clan.get_member(username)
        if not member:
            return await ctx.send(message["player_not_in_clan"][setting.LANGUAGE].format(player.name))
            print(f"    - Answer sent. Took: {time.time() - start_time:.2f}s")
        user_clan_exp = member['exp']
        user_rank = member['rank']
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
        clan_info_embed.add_field(
            name=rank_header, value=f"{user_rank} {rank_emoji}")
        clan_info_embed.add_field(name=exp_header, value=f"{user_clan_exp:,}")
        if player.private_profile:
            clan_info_embed.add_field(
                name=total_exp_header, value=private_profile_header)
        else:
            clan_info_embed.add_field(
                name=total_exp_header, value=f"{player.exp:,}")

        print(f"    - Answer sent. Took: {time.time() - start_time:.2f}s")
        return await ctx.send(content=None, embed=clan_info_embed)

    @commands.command(aliases=['ranksupdate', 'upranks'])
    async def ranks(self, ctx):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'ranks'.")
        start_time = time.time()
        exp_general = 500_000_000
        exp_captain = 225_000_000
        exp_lieutenant = 125_000_000
        exp_seargent = 50_000_000

        rank_emoji = {
            'Corporal': setting.CLAN_SETTINGS['Corporal']['Emoji'],
            'Sergeant': setting.CLAN_SETTINGS['Sergeant']['Emoji'],
            'Lieutenant': setting.CLAN_SETTINGS['Lieutenant']['Emoji'],
            'Captain': setting.CLAN_SETTINGS['Captain']['Emoji'],
            'General': setting.CLAN_SETTINGS['General']['Emoji'],
        }

        ranks_embed = discord.Embed(title="__Ranks a Atualizar__",
                                    description=" ",)
        found = False
        clan = rs3clans.Clan(setting.CLAN_NAME, set_exp=False)
        for member in clan.member.items():
            if member[1]['exp'] >= exp_general and member[1]['rank'] == 'Captain':
                ranks_embed.add_field(name=member[0],
                                      value=f"Capitão {rank_emoji['Captain']} > General {rank_emoji['General']}\n**__Exp:__** {member[1]['exp']:,}\n" + (
                                          "_\\" * 15) + "_",
                                      inline=False)
                found = True
            elif member[1]['exp'] >= exp_captain and member[1]['rank'] == 'Lieutenant':
                ranks_embed.add_field(name=member[0],
                                      value=f"Tenente {rank_emoji['Lieutenant']} > Capitão {rank_emoji['Captain']}\n**__Exp:__** {member[1]['exp']:,}\n" + (
                                          "_\\" * 15) + "_",
                                      inline=False)
                found = True
            elif member[1]['exp'] >= exp_lieutenant and member[1]['rank'] == 'Sergeant':
                ranks_embed.add_field(name=member[0],
                                      value=f"Sargento {rank_emoji['Sergeant']} > Tenente {rank_emoji['Lieutenant']}\n**__Exp:__** {member[1]['exp']:,}\n" + (
                                          "_\\" * 15) + "_",
                                      inline=False)
                found = True
            elif member[1]['exp'] >= exp_seargent and member[1]['rank'] == 'Corporal':
                ranks_embed.add_field(name=member[0],
                                      value=f"Cabo {rank_emoji['Corporal']} > Sargento {rank_emoji['Sergeant']}\n**__Exp:__** {member[1]['exp']:,}\n" + (
                                          "_\\" * 15) + "_",
                                      inline=False)
                found = True
        if not found:
            ranks_embed.add_field(name="Nenhum Rank a ser atualizado no momento :)",
                                  value=separator,
                                  inline=False)
        print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
        return await ctx.send(embed=ranks_embed)


def setup(bot):
    bot.add_cog(ClanCommands(bot))
