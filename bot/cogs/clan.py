import rs3clans
import discord
from discord.ext import commands

from bot.bot_client import Bot
from bot.utils.tools import separator
from bot.utils.context import Context


class Clan(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['clan'])
    async def clan_detail_info(self, ctx: Context, *, clan_name: str):
        try:
            clan = rs3clans.Clan(name=clan_name, set_exp=True)
        except ConnectionError:
            return await ctx.send(f"Houve um erro ao tentar conectar a API da Jagex. Tente novamente mais tarde.")
        except rs3clans.ClanNotFoundError:
            return await ctx.send(f"O clã '{clan_name}' não existe.")
        clan_leader = None
        for member in clan:
            if member.rank == 'Owner':
                clan_leader = member.name
        clan_url = clan.name.replace(' ', '%20')
        clan_embed = discord.Embed(
            title=clan.name,
            color=discord.Color.green(),
            url=f'http://services.runescape.com/m=clan-home/clan/{clan_url}'
        )
        clan_embed.set_author(name='RuneClan', url=f'https://runeclan.com/clan/{clan_url}')
        clan_embed.set_thumbnail(url=f'http://services.runescape.com/m=avatar-rs/{clan_url}/clanmotif.png')
        clan_embed.add_field(name="Exp Total", value=f'{clan.exp:,}')
        clan_embed.add_field(name="Membros", value=str(clan.count))
        clan_embed.add_field(name="Líder", value=clan_leader)
        clan_embed.add_field(name="Exp Média por Membro", value=f'{clan.avg_exp:,.0f}')
        return await ctx.send(embed=clan_embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['claninfo', 'clanexp', 'claexp', 'clainfo', 'clãexp', 'clãinfo'])
    async def clan_user_info(self, ctx: Context, *, username: str):
        try:
            player = rs3clans.Player(name=username, runemetrics=True)
        except ConnectionError:
            return await ctx.send(f"Houve um erro ao tentar conectar a API da Jagex. Tente novamente mais tarde.")
        if not player.exists:
            return await ctx.send(f"Jogador '{player.name}' não existe.")
        if not player.clan:
            return await ctx.send(f"Jogador '{player.name}' não está em um clã.")
        user_clan = rs3clans.Clan(name=player.clan)
        member = user_clan.get_member(username)
        user_clan_exp = member.exp
        user_rank = member.rank
        display_username = player.name
        if self.bot.setting.show_titles:
            if player.suffix:
                display_username = f"{player.name} {player.title}"
            else:
                display_username = f"{player.title} {player.name}"

        user_url_name = player.name.replace(" ", "%20")
        user_url_clan = player.clan.replace(" ", "%20")
        icon_url = f"https://secure.runescape.com/m=avatar-rs/{user_url_name}/chat.png"
        runeclan_url = f"https://runeclan.com/user/{user_url_name}"
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
            value=f"{user_clan_exp:,}",
            inline=False
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

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['ranksupdate', 'upranks', 'rank'])
    async def ranks(self, ctx: Context):
        exp_general = 500_000_000
        exp_captain = 225_000_000
        exp_lieutenant = 125_000_000
        exp_seargent = 50_000_000

        rank_emoji = {
            'Recruit': self.bot.setting.clan_settings['Recruit']['Emoji'],
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

        for member in clan:
            if len(ranks_embed.fields) >= 20:
                await ctx.send('Muitos ranks a serem atualizados, enviando apenas os 20 primeiros.')
                break

            if member.rank == 'Recruit':
                ranks_embed.add_field(
                    name=member.name,
                    value=f"Recruta {rank_emoji['Recruit']} ❯ Cabo {rank_emoji['Corporal']}\n"
                    f"**__Exp:__** {member.exp:,}\n{separator}",
                    inline=False)
                found = True
            elif member.exp >= exp_general and member.rank == 'Captain':
                ranks_embed.add_field(
                    name=member.name,
                    value=f"Capitão {rank_emoji['Captain']} ❯ General {rank_emoji['General']}\n"
                    f"**__Exp:__** {member.exp:,}\n{separator}",
                    inline=False)
                found = True
            elif member.exp >= exp_captain and member.rank == 'Lieutenant':
                ranks_embed.add_field(
                    name=member.name,
                    value=f"Tenente {rank_emoji['Lieutenant']} ❯ Capitão {rank_emoji['Captain']}\n"
                    f"**__Exp:__** {member.exp:,}\n{separator}",
                    inline=False)
                found = True
            elif member.exp >= exp_lieutenant and member.rank == 'Sergeant':
                ranks_embed.add_field(
                    name=member.name,
                    value=f"Sargento {rank_emoji['Sergeant']} ❯ Tenente {rank_emoji['Lieutenant']}\n"
                    f"**__Exp:__** {member.exp:,}\n{separator}",
                    inline=False)
                found = True
            elif member.exp >= exp_seargent and member.rank == 'Corporal':
                ranks_embed.add_field(
                    name=member.name,
                    value=f"Cabo {rank_emoji['Corporal']} ❯ Sargento {rank_emoji['Sergeant']}\n"
                    f"**__Exp:__** {member.exp:,}\n{separator}",
                    inline=False)
                found = True

        if not found:
            ranks_embed.add_field(
                name="Nenhum Rank a ser atualizado no momento :)",
                value=separator,
                inline=False)

        return await ctx.send(embed=ranks_embed)


def setup(bot):
    bot.add_cog(Clan(bot))
