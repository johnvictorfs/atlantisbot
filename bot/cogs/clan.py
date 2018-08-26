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
        display_username = user.name
        if setting.SHOW_TITLES:
            if user.suffix:
                display_username = f"{user.name} {user.title}"
            else:
                display_username = f"{user.title} {user.name}"
        user_rank = user_clan.member[user.name]['rank']

        user_url_name = user.name.replace(" ", "%20")
        user_url_clan = user.clan.replace(" ", "%20")
        icon_url = f"https://secure.runescape.com/m=avatar-rs/{user_url_name}/chat.png"
        runeclan_url = f"https://runeclan.com/user/{user_url_name}"
        clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{user_url_clan}/clanmotif.png"

        embed_title = "RuneClan"
        rank_header = "__Rank__"

        clan_header = "__Clan__"
        exp_header = "__Clan Exp__"
        total_exp_header = "__Total Exp__"
        private_profile_header = "Unavailable - Private Profile"

        user_rank_f = setting.CLAN_SETTINGS[user_rank]
        rank_emoji = user_rank_f['Emoji']
        if setting.LANGUAGE == 'Portuguese':
            user_rank = user_rank_f['Translation']
            clan_header = "__Clã__"
            exp_header = "__Exp no Clã__"
            total_exp_header = "__Exp Total__"
            private_profile_header = "Indisponível - Perfil Privado"

        clan_info_embed = discord.Embed(title=embed_title,
                                        description="",
                                        color=discord.Colour.dark_blue(),
                                        url=runeclan_url,
                                        )

        clan_info_embed.set_author(icon_url=icon_url, name=display_username)
        clan_info_embed.set_thumbnail(url=clan_banner_url)
        clan_info_embed.add_field(name=clan_header, value=user.clan)
        clan_info_embed.add_field(name=rank_header, value=f"{user_rank} {rank_emoji}")
        clan_info_embed.add_field(name=exp_header, value=f"{user_clan_exp:,}")
        if user.private_profile:
            clan_info_embed.add_field(name=total_exp_header, value=private_profile_header)
        else:
            clan_info_embed.add_field(name=total_exp_header, value=f"{user.exp:,}")

        await ctx.send(content=None, embed=clan_info_embed)
        print("    - Answer sent.")


def setup(bot):
    bot.add_cog(ClanCommands(bot))
