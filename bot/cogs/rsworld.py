import random
import re

from discord.ext import commands
from bs4 import BeautifulSoup
import aiohttp
import discord
import rs3clans

from bot.bot_client import Bot
from bot.utils.context import Context


async def grab_clan_id(clan_name: str):
    """
    Gets the ID of a RuneScape 3 Clan
    """
    url = f"http://services.runescape.com/m=clan-hiscores/l=3/members.ws?clanName={clan_name}"

    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            source = await r.text()
            soup = BeautifulSoup(source, 'lxml')

            clan_id = soup.find('input', {'name': 'clanId'})
            if clan_id:
                return clan_id.get('value')


async def grab_world(player_name: str, player_clan: str):
    # clan_id = grab_clan_id(player_name)
    clan_id = 184644  # Atlantis Clan ID

    player_search = player_name.replace(' ', '+')

    base_url = "http://services.runescape.com/m=clan-hiscores/l=3/a=254/members.ws"
    search_url = f"{base_url}?expandPlayerName={player_search}&clanId={clan_id}&ranking=-1&pageSize=1&submit=submit"

    async with aiohttp.ClientSession() as cs:
        async with cs.get(search_url) as r:
            source = await r.text()

            soup = BeautifulSoup(source, 'lxml')
            list_members = soup.findAll('div', {'class': 'membersListRow'})

            for member in list_members:
                row_name = member.find('span', attrs={'class': 'name'})

                # Remove nb spaces
                if row_name.text.lower().replace(u'\xa0', ' ') == player_name.lower():
                    world = member.find('span', attrs={'class': 'world'}).text
                    world = re.search(r'\d+', world)
                    if not world:
                        return "Offline"
                    return int(world.group())


def f2p_worlds(worlds: list):
    """
    Filters a list of worlds to a list only containing f2p worlds
    """
    return [world for world in worlds if world['f2p'] and not world['vip']]


def p2p_worlds(worlds: list):
    """
    Filters a list of worlds to a list only containing p2p worlds
    """
    return [world for world in worlds if not world['f2p'] and not world['vip']]


def filtered_worlds(worlds: list, f2p_worlds=False, legacy_worlds=False, language='pt', worlds_left=None, **kwargs) -> list:
    """
    Filter list worlds based on arguments passed
    """
    world_list = []

    for world in worlds:
        if not world['vip'] and world['requirement'] == 0:
            if world['legacy'] and not legacy_worlds:
                continue
            if world['f2p'] and not f2p_worlds:
                continue
            if world['language'] == language:
                world_list.append(world)

    return world_list


def get_world(worlds: list, number: int):
    """
    Gets a specific world dict from a list of world dicts
    """
    for world in worlds:
        if world['world'] == number:
            return world


def random_world(worlds: list):
    """
    Gets a random world from a list of worlds
    """
    return random.choice(worlds)


class RsWorld(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=['world'])
    async def rsworld(self, ctx: Context, *, player_name: str):
        player = rs3clans.Player(player_name)

        if not player.exists:
            return await ctx.send(f"Jogador {player_name} não existe.")
        if not player.clan:
            return await ctx.send(f"Jogador {player_name} não está em um clã.")

        world = await grab_world(player.name, player.clan)
        world_display = "Offline" if (world == "Offline" or not world) else f"**Mundo:** {world}"
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


def setup(bot):
    bot.add_cog(RsWorld(bot))
