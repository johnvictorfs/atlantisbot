import discord
import aiohttp

from operator import itemgetter

from discord.ext import commands


class ClanHiscores:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[
        'ptbrrankings',
        'ptrankings',
        'brrankings',
        'br_rankings'
        'pt_rankings'
        'brhiscores',
        'pthiscores',
        'ptbr_hiscores',
        'pt_hiscores',
        'br_hiscores',
    ])
    async def ptbr_rankings(self, ctx: commands.Context, num_clans: int = 10):
        base_url = 'https://nriver.pythonanywhere.com'
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'{base_url}/api/clan/list/') as r:
                clans = await r.json()
                if r.status != 200:
                    return await ctx.send(f'Erro **{r.status}** ao se conectar a API dos Rankings de Clãs Pt-Br.')
        rankings_embed = discord.Embed(title='Ranking de Clãs Pt-Br', color=discord.Color.green())
        # Sorting clans by ranking
        clans = sorted(clans, key=itemgetter('rank'))
        for clan in clans[:num_clans]:
            if clan['approved']:
                rankings_embed.add_field(
                    name=f'{clan["rank"]}- {clan["name"]}',
                    value=f'{clan["exp"]:,.0f}',
                    inline=False
                )
        rankings_embed.set_footer(text='A exp dos Clãs é atualizada a cada 5 minutos.')
        rankings_embed.set_thumbnail(url='https://cdn.countryflags.com/thumbs/brazil/flag-round-250.png')
        return await ctx.send(embed=rankings_embed)


def setup(bot):
    bot.add_cog(ClanHiscores(bot))
