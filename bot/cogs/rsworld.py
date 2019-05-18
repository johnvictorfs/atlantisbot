import re

from discord.ext import commands
from bs4 import BeautifulSoup
import discord
import rs3clans
import requests

from bot.bot_client import Bot


class RsWorld(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=['world'])
    async def rsworld(self, ctx: commands.Context, *, player_name: str):
        player = rs3clans.Player(player_name)

        if not player.exists:
            return await ctx.send(f"Jogador {player_name} não existe.")
        if not player.clan:
            return await ctx.send(f"Jogador {player_name} não está em um clã.")

        world = self.grab_world(player)
        world_display = "Offline" if world == "Offline" else f"**Mundo:** {world}"
        nb = '\u200B'
        color = discord.Colour.green()
        if world == "Offline":
            color = discord.Colour.dark_red()

        embed = discord.Embed(title=nb, description=world_display, color=color)

        url_name = player.name.replace(' ', '%20')
        url_clan = player.clan.replace(' ', '%20')
        embed.set_author(name=player.name, icon_url=f"https://secure.runescape.com/m=avatar-rs/{url_name}/chat.png")
        embed.set_thumbnail(url=f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{url_clan}/clanmotif.png")

        return await ctx.send(embed=embed)

    @staticmethod
    def grab_clan_id(clan_name: str):
        url = f"http://services.runescape.com/m=clan-hiscores/l=3/members.ws?clanName={clan_name}"
        source = requests.get(url).content
        soup = BeautifulSoup(source.decode('utf-8', 'ignore'), 'lxml')

        clan_id = soup.find('input', {'name': 'clanId'})
        if clan_id:
            return clan_id.get('value')

    def grab_world(self, player: rs3clans.Player):

        clan_id = self.grab_clan_id(player.clan)

        player_search = player.name.replace(' ', '+')

        base_url = "http://services.runescape.com/m=clan-hiscores/l=3/a=254/members.ws"
        search_url = f"{base_url}?expandPlayerName={player_search}&clanId={clan_id}&ranking=-1&pageSize=1&submit=submit"

        source = requests.get(search_url).content
        soup = BeautifulSoup(source.decode('utf-8', 'ignore'), 'lxml')
        list_members = soup.findAll('div', {'class': 'membersListRow'})

        for member in list_members:
            row_name = member.find('span', attrs={'class': 'name'})
            if row_name.text.lower() == player.name.replace(' ', '').lower():
                world = member.find('span', attrs={'class': 'world'}).text
                world = re.search(r'\d+', world)
                if not world:
                    return "Offline"
                return int(world.group())


def setup(bot):
    bot.add_cog(RsWorld(bot))
