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
    async def clan_user_info(self, ctx, *, username):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'clan_user_exp'.")

        player = rs3.Player(name=username)
        if not player.exists:
            if setting.LANGUAGE == 'Portuguese':
                await ctx.send(f"Jogador '{player.name}' não existe.")
                return
            else:
                await ctx.send(f"Player '{player.name}' does not exist.")
                return
        try:
            user_clan = rs3.Clan(name=player.clan)
        except rs3.ClanNotFoundError:
            if setting.LANGUAGE == 'Portuguese':
                await ctx.send(f"Jogador '{player.name}' não se encontra em um Clã.")
                return
            else:
                await ctx.send(f"Player '{player.name}' is not in a Clan.")
                return
        try:
            user_clan_exp = user_clan.member[player.name]['exp']
        except KeyError:
            if player.private_profile:
                if setting.LANGUAGE == 'Portuguese':
                    await ctx.send(f"Jogador '{player.name}' tem seu perfil privado, portanto seu nome precisa ser "
                                   f"digitado exatamente da forma como está no jogo ('NRiver' ao invés de 'nriver' por"
                                   f"exemplo)")
                    return
                else:
                    await ctx.send(f"Player '{player.name}' has a private profile, thus its username has to be input "
                                   f"case-sensitively ('NRiver' instead of 'nriver' for example.)")
                    return
            else:
                if setting.LANGUAGE == 'Portuguese':
                    await ctx.send(f"Jogador '{player.name}' não se encontra em um Clã.")
                    return
                else:
                    await ctx.send(f"Player '{player.name}' is not in a Clan.")
                    return

        display_username = player.name
        if setting.SHOW_TITLES:
            if player.suffix:
                display_username = f"{player.name} {player.title}"
            else:
                display_username = f"{player.title} {player.name}"
        user_rank = user_clan.member[player.name]['rank']

        user_url_name = player.name.replace(" ", "%20")
        user_url_clan = player.clan.replace(" ", "%20")
        icon_url = f"https://secure.runescape.com/m=avatar-rs/{user_url_name}/chat.png"
        runeclan_url = f"https://runeclan.com/player/{user_url_name}"
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
        clan_info_embed.add_field(name=clan_header, value=player.clan)
        clan_info_embed.add_field(name=rank_header, value=f"{user_rank} {rank_emoji}")
        clan_info_embed.add_field(name=exp_header, value=f"{user_clan_exp:,}")
        if player.private_profile:
            clan_info_embed.add_field(name=total_exp_header, value=private_profile_header)
        else:
            clan_info_embed.add_field(name=total_exp_header, value=f"{player.exp:,}")

        await ctx.send(content=None, embed=clan_info_embed)
        print("    - Answer sent.")


def setup(bot):
    bot.add_cog(ClanCommands(bot))
