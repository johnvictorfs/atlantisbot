import time

import rs3clans
import discord
from discord.ext import commands

from .utils import separator


class ClanCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['claninfo', 'clanexp', 'claexp', 'clainfo', 'clãexp', 'clãinfo', 'clan', 'cla'])
    async def clan_user_info(self, ctx, *, username: str):
        try:
            player = rs3clans.Player(name=username, runemetrics=True)
        except ConnectionError:
            return await ctx.send(f"Houve um erro tentando conectar a API da Jagex. Tente novamente mais tarde. "
                                  f"(Código {player.details_status_code})")
        if not player.exists:
            return await ctx.send(f"Jogador '{player.name}' não existe.")
        if not player.clan:
            return await ctx.send(f"Jogador '{player.name}' não está em um clã.")
        user_clan = rs3clans.Clan(name=player.clan)
        member = user_clan.get_member(username)
        user_clan_exp = member['exp']
        user_rank = member['rank']
        display_username = player.name
        if self.bot.setting.show_titles:
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
        clan_header = "__Clã__"
        exp_header = "__Exp no Clã__"
        total_exp_header = "__Exp Total__"
        private_profile_header = "Indisponível - Perfil Privado"

        rank_emoji = self.bot.setting.clan_settings[user_rank]['Emoji']
        user_rank = self.bot.setting.clan_settings[user_rank]['Translation']

        clan_info_embed = discord.Embed(
            title=embed_title,
            description="",
            color=discord.Colour.dark_blue(),
            url=runeclan_url,
        )

        clan_info_embed.set_author(
            icon_url=icon_url, name=display_username
        )
        clan_info_embed.set_thumbnail(
            url=clan_banner_url
        )
        clan_info_embed.add_field(
            name=clan_header,
            value=player.clan
        )
        clan_info_embed.add_field(
            name=rank_header,
            value=f"{user_rank} {rank_emoji}"
        )
        clan_info_embed.add_field(
            name=exp_header,
            value=f"{user_clan_exp:,}"
        )
        if player.private_profile:
            clan_info_embed.add_field(
                name=total_exp_header,
                value=private_profile_header
            )
        else:
            clan_info_embed.add_field(
                name=total_exp_header,
                value=f"{player.exp:,}"
            )
        return await ctx.send(content=None, embed=clan_info_embed)

    @commands.cooldown(1, 5)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['ranksupdate', 'upranks', 'rank'])
    async def ranks(self, ctx):
        exp_general = 500_000_000
        exp_captain = 225_000_000
        exp_lieutenant = 125_000_000
        exp_seargent = 50_000_000

        rank_emoji = {
            'Corporal': self.bot.setting.clan_settings['Corporal']['Emoji'],
            'Sergeant': self.bot.setting.clan_settings['Sergeant']['Emoji'],
            'Lieutenant': self.bot.setting.clan_settings['Lieutenant']['Emoji'],
            'Captain': self.bot.setting.clan_settings['Captain']['Emoji'],
            'General': self.bot.setting.clan_settings['General']['Emoji'],
        }

        ranks_embed = discord.Embed(
            title="__Ranks a Atualizar__",
            description=" ", )
        found = False
        clan = rs3clans.Clan(self.bot.setting.clan_name, set_exp=False)
        for member in clan.member.items():
            if member[1]['exp'] >= exp_general and member[1]['rank'] == 'Captain':
                ranks_embed.add_field(
                    name=member[0],
                    value=f"Capitão {rank_emoji['Captain']} > General {rank_emoji['General']}\n"
                          f"**__Exp:__** {member[1]['exp']:,}\n{separator}",
                    inline=False)
                found = True
            elif member[1]['exp'] >= exp_captain and member[1]['rank'] == 'Lieutenant':
                ranks_embed.add_field \
                    (name=member[0],
                     value=f"Tenente {rank_emoji['Lieutenant']} > Capitão {rank_emoji['Captain']}\n"
                           f"**__Exp:__** {member[1]['exp']:,}\n{separator}",
                     inline=False)
                found = True
            elif member[1]['exp'] >= exp_lieutenant and member[1]['rank'] == 'Sergeant':
                ranks_embed.add_field(
                    name=member[0],
                    value=f"Sargento {rank_emoji['Sergeant']} > Tenente {rank_emoji['Lieutenant']}\n"
                          f"**__Exp:__** {member[1]['exp']:,}\n{separator}",
                    inline=False)
                found = True
            elif member[1]['exp'] >= exp_seargent and member[1]['rank'] == 'Corporal':
                ranks_embed.add_field(
                    name=member[0],
                    value=f"Cabo {rank_emoji['Corporal']} > Sargento {rank_emoji['Sergeant']}\n"
                          f"**__Exp:__** {member[1]['exp']:,}\n{separator}",
                    inline=False)
                found = True
        if not found:
            ranks_embed.add_field(
                name="Nenhum Rank a ser atualizado no momento :)",
                value=separator,
                inline=False)
        return await ctx.send(embed=ranks_embed)


def setup(bot):
    bot.add_cog(ClanCommands(bot))
