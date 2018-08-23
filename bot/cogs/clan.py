# Standard lib imports
import json

# Non-Standard lib imports
import rs3clans as rs3
import discord
from discord.ext import commands

# Local imports
import definesettings as setting


class ClanCommands:

    def __init__(self, bot):
        self.bot = bot

    # def on_member_join(self, member):
    #     print(f'{member.nick} joined {member.guild} at {member.joined_at}')

    @commands.command(aliases=['claninfo', 'clanexp'])
    async def clan_user_exp(self, ctx, *, username):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'clan_user_exp'.", sep='')
        with open('clan_settings.json') as f:
            clan_settings = json.load(f)
        user = rs3.Player(name=username)
        try:
            user_clan = rs3.Clan(name=user.clan)
        except rs3.ClanNotFoundError:
            if setting.LANGUAGE == 'Portuguese':
                await ctx.send(f"Jogador '{user.name}' não se encontra em um Clã.")
                return
            else:
                await ctx.send(f"Player '{user.name}' is not in a Clan.")
                return
            pass
        try:
            user_clan_exp = user_clan.member[user.name]['exp']
        except KeyError:
            if user.private_profile:
                if setting.LANGUAGE == 'Portuguese':
                    await ctx.send(f"Jogador '{user.name}' tem seu perfil privado, portanto seu nome precisa ser "
                                   f"digitado exatamente da forma como está no jogo ('NRiver' ao invés de 'nriver' por"
                                   f"exemplo)")
                    return
                else:
                    await ctx.send(f"Player '{user.name}' has a private profile, thus its username has to be input "
                                   f"case-sensitively ('NRiver' instead of 'nriver' for example.)")
                    return
            else:
                if setting.LANGUAGE is 'Portuguese':
                    await ctx.send(f"Jogador '{user.name}' não foi encontrado.")
                    return
                else:
                    await ctx.send(f"Player '{user.name}' not found.")
                    return
        if setting.SHOW_TITLES:
            if user.suffix:
                display_username = f"{user.name} {user.title}"
            else:
                display_username = f"{user.title} {user.name}"
        else:
            display_username = user.name
        user_rank = user_clan.member[user.name]['rank']
        icon_url = setting.ICON_URL.format(user.name).replace(" ", "%20")
        runeclan_url = setting.RUNECLAN_URL.format(user.name).replace(" ", "%20")
        clan_banner = setting.CLAN_BANNER_URL.format(user.clan).replace(" ", "%20")

        embed_title = "RuneClan"
        clan_header = "__Clan__"
        rank_header = "__Rank__"
        exp_header = "__Clan Exp__"
        total_exp_header = "__Total Exp__"
        private_profile_header = "Unavailable - Private Profile"

        for rank in clan_settings['clan_ranks']:
            if user_rank == rank['Rank']:
                rank_emoji = rank['Emoji']
                if setting.LANGUAGE == 'Portuguese':
                    user_rank = rank['Translation']
                    embed_title = "RuneClan"
                    clan_header = "__Clã__"
                    rank_header = "__Rank__"
                    exp_header = "__Exp no Clã__"
                    total_exp_header = "__Exp Total__"
                    private_profile_header = "Indisponível - Perfil Privado"

        clan_info_embed = discord.Embed(title=embed_title,
                                        description="",
                                        color=discord.Colour.dark_blue(),
                                        url=runeclan_url,
                                        )

        clan_info_embed.set_author(icon_url=icon_url, name=display_username)
        clan_info_embed.set_thumbnail(url=clan_banner)
        clan_info_embed.add_field(name=clan_header, value=user.clan)
        clan_info_embed.add_field(name=rank_header, value=f"{user_rank} {rank_emoji}")
        clan_info_embed.add_field(name=exp_header, value=f"{user_clan_exp:,}")
        if user.private_profile:
            clan_info_embed.add_field(name=total_exp_header, value=private_profile_header)
        else:
            clan_info_embed.add_field(name=total_exp_header, value=f"{user.exp:,}")

        await ctx.send(content=None, embed=clan_info_embed)
        print(" - Answer sent.")


def setup(bot):
    bot.add_cog(ClanCommands(bot))
