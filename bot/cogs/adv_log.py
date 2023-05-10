from typing import Optional
from io import StringIO
import urllib.parse as urlparse
import asyncio
import csv
import traceback
import re
import feedparser

from atlantisbot_api.models import PlayerActivities, AdvLogState
from discord.ext import tasks, commands
import aiohttp
import discord

from bot.bot_client import Bot


class AdvLog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        if self.bot.setting.mode == "prod":
            self.adv_log.start()

    def cog_unload(self):
        if self.bot.setting.mode == "prod":
            self.adv_log.cancel()

    @staticmethod
    def is_advlog_active():
        state = AdvLogState.object()
        return state.active

    @tasks.loop(seconds=15)
    async def adv_log(self):
        if self.is_advlog_active():
            async with aiohttp.ClientSession() as cs:
                try:
                    for get_clan in self.bot.setting.advlog_clans:
                        clan_name = get_clan.get("name").replace(" ", "%20")
                        clan_list: list = await self.retrieve_clan_list(cs, clan_name)
                        channel: discord.TextChannel = self.bot.get_channel(
                            get_clan.get("chat")
                        )
                        banner = f"http://services.runescape.com/m=avatar-rs/{clan_name}/clanmotif.png"

                        for player in clan_list[1:]:
                            player = player[0]
                            entries = await self.retrieve_activities(cs, player)
                            if not entries:
                                continue
                            for entry in entries:
                                if not self.is_advlog_active():
                                    await asyncio.sleep(10)
                                    break
                                parsed_url = urlparse.urlparse(entry.get("guid"))
                                entry_id = urlparse.parse_qs(parsed_url.query).get(
                                    "id"
                                )[0]

                                exists = PlayerActivities.objects.filter(
                                    activities_id=entry_id
                                ).first()
                                if exists:
                                    continue
                                PlayerActivities.objects.create(activities_id=entry_id)
                                title = entry.get("title")
                                description = entry.get("description")
                                try:
                                    description_exp = int(
                                        re.findall(r"\d+", entry.get("description"))[0]
                                    )
                                    if description_exp:
                                        description = description.replace(
                                            str(description_exp), f"{description_exp:,}"
                                        )
                                    title_exp = int(
                                        re.findall(r"\d+", entry.get("title"))[0]
                                    )
                                    if title_exp:
                                        title = title.replace(
                                            str(title_exp), f"{title_exp:,} "
                                        )
                                except IndexError:
                                    pass
                                # Removing non-breaking spaces from the player's name, since they would break the URL
                                # Source: https://stackoverflow.com/a/52254293
                                player_icon_url = " ".join(player.split()).replace(
                                    " ", "%20"
                                )
                                icon_url = f"https://secure.runescape.com/m=avatar-rs/{player_icon_url}/chat.png"

                                embed = discord.Embed(
                                    title=title, description=description
                                )
                                embed.set_author(name=player, icon_url=icon_url)
                                embed.set_thumbnail(url=banner)
                                pub_date = entry.get("published_parsed")
                                if pub_date:
                                    embed.set_footer(
                                        text=f"• {pub_date.tm_mday}/{pub_date.tm_mon}/{pub_date.tm_year}"
                                    )
                                await channel.send(embed=embed)
                                await asyncio.sleep(5)
                except Exception as e:
                    await self.bot.send_logs(e, traceback.format_exc())

    @adv_log.before_loop
    async def before_adv_log(self):
        await self.bot.wait_until_ready()

    @staticmethod
    async def retrieve_activities(
        cs: aiohttp.ClientSession, player: str
    ) -> Optional[list]:
        url = f"http://services.runescape.com/m=adventurers-log/l=3/a=869/rssfeed?searchName={player}"
        async with cs.get(url) as r:
            text = await r.text()
            feed = feedparser.parse(text)
            if r.status == 200:
                return feed.get("entries")

        return None

    @staticmethod
    async def retrieve_clan_list(cs: aiohttp.ClientSession, clan_name: str) -> list:
        clan_name = clan_name.replace(" ", "%20")
        clan = f"http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName={clan_name}"
        async with cs.get(clan) as r:
            clan_csv = await r.text()
            return list(csv.reader(StringIO(clan_csv), delimiter=","))


async def setup(bot):
    await bot.add_cog(AdvLog(bot))
