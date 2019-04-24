import asyncio
import csv
import traceback
import re
import ast
import datetime
import feedparser
import urllib.parse as urlparse
from io import StringIO

from discord.ext import commands
import aiohttp
import discord

from bot.bot_client import Bot
from bot.orm.models import PlayerActivities, AdvLogState


class AdvLog(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        # if self.bot.setting.mode == 'prod':
        #     self.advlog_task = self.bot.loop.create_task(self.advlog())
        self.advlog_task2 = self.bot.loop.create_task(self.adv_log())

    def cog_unload(self):
        self.advlog_task2.cancel()
        # self.advlog_task.cancel()

    async def adv_log(self):
        await self.bot.wait_until_ready()

        while True:
            with self.bot.db_session() as session:
                state = session.query(AdvLogState).first()
                if not state:
                    state = AdvLogState(messages=True)
                    session.add(state)
                    session.commit()
                current_state = state.messages
            if not current_state:
                await asyncio.sleep(60)
                continue
            async with aiohttp.ClientSession() as cs:
                try:
                    for get_clan in self.bot.setting.advlog_clans:
                        clan_name = get_clan.get('name').replace(' ', '%20')
                        clan_list: list = await self.retrieve_clan_list(cs, clan_name)
                        channel: discord.TextChannel = self.bot.get_channel(get_clan.get('chat'))
                        banner = f"http://services.runescape.com/m=avatar-rs/{clan_name}/clanmotif.png"

                        for player in clan_list[1:]:
                            player = player[0]
                            entries = await self.retrieve_activities(cs, player)
                            if not entries:
                                continue
                            for entry in entries:
                                parsed_url = urlparse.urlparse(entry.get('guid'))
                                entry_id = urlparse.parse_qs(parsed_url.query).get('id')[0]
                                with self.bot.db_session() as session:
                                    exists = session.query(PlayerActivities).filter_by(activities_id=entry_id).first()
                                if exists:
                                    continue
                                with self.bot.db_session() as session:
                                    session.add(PlayerActivities(activities_id=entry_id))
                                title = entry.get('title')
                                description = entry.get('description')
                                try:
                                    description_exp = int(re.findall(r'\d+', entry.get('description'))[0])
                                    if description_exp:
                                        description = description.replace(str(description_exp), f"{description_exp:,}")
                                    title_exp = int(re.findall(r'\d+', entry.get('title'))[0])
                                    if title_exp:
                                        title = title.replace(str(title_exp), f"{title_exp:,} ")
                                except IndexError:
                                    pass
                                # Removing non-breaking spaces from the player's name, since they would break the URL
                                # Source: https://stackoverflow.com/a/52254293
                                player_icon_url = ' '.join(player.split()).replace(' ', '%20')
                                icon_url = f"https://secure.runescape.com/m=avatar-rs/{player_icon_url}/chat.png"

                                embed = discord.Embed(title=title, description=description)
                                embed.set_author(name=player, icon_url=icon_url)
                                embed.set_thumbnail(url=banner)
                                pub_date = entry.get('pubDate')
                                if pub_date:
                                    embed.set_footer(text=pub_date.replace(' 00:00:00 GMT', ''))
                                await channel.send(embed=embed)
                                await asyncio.sleep(5)
                except Exception as e:
                    await self.bot.send_logs(e, traceback.format_exc())
                    await asyncio.sleep(60 * 3)
                await asyncio.sleep(15)

    @staticmethod
    async def retrieve_activities(cs: aiohttp.ClientSession, player: str) -> list:
        url = f'http://services.runescape.com/m=adventurers-log/l=3/a=869/rssfeed?searchName={player}'
        async with cs.get(url) as r:
            text = await r.text()
            feed = feedparser.parse(text)
            if r.status == 200:
                return feed.get('entries')

    async def advlog(self):
        await self.bot.wait_until_ready()

        while True:
            try:
                with self.bot.db_session() as session:
                    state = session.query(AdvLogState).first()
                    if not state:
                        state = AdvLogState(messages=True)
                        session.add(state)
                        session.commit()
                    current_state = state.messages
                if not current_state:
                    await asyncio.sleep(60)
                    continue
                async with aiohttp.ClientSession() as cs:
                    for get_clan in self.bot.setting.advlog_clans:
                        clan = get_clan.get('name')
                        clan_name = get_clan.get('name').replace(' ', '%20')
                        clan_list = await self.retrieve_clan_list(cs, get_clan.get('name'))

                        print(
                            f"Checking for new adventurer's log entries from clanmates at {datetime.datetime.utcnow()}.")

                        channel = self.bot.get_channel(get_clan.get('chat'))
                        banner = f"http://services.runescape.com/m=avatar-rs/{clan_name}/clanmotif.png"

                        with self.bot.db_session() as session:
                            all_activities = session.query(PlayerActivities).filter_by(clan=clan).all()
                            old_activities = {}
                            if all_activities:
                                for act in all_activities:
                                    if not max(act.name in member for member in clan_list):
                                        print(f"Removing {act.name} from Adv. Log database.")
                                        session.delete(act)
                                        session.commit()
                                    act_list = ast.literal_eval(act.activities)
                                    old_activities[act.name] = act_list

                            for player in clan_list[1:]:
                                player = player[0]
                                # Removing non-breaking spaces from the player's name, since they would break the URL
                                # Source: https://stackoverflow.com/a/52254293
                                player_icon_url = ' '.join(player.split()).replace(' ', '%20')
                                icon_url = f"https://secure.runescape.com/m=avatar-rs/{player_icon_url}/chat.png"
                                activities = await self.retrieve_activities(cs, player)

                                if not session.query(PlayerActivities).filter_by(name=player).first():
                                    print(f'Adding {player} to Adv. Log database.')
                                    new_player = PlayerActivities(name=player, activities=str(activities), clan=clan)
                                    session.add(new_player)
                                    session.commit()
                                    continue

                                for activity in activities:
                                    if activity not in old_activities[player]:
                                        text = activity.get('text')
                                        details = activity.get('details')
                                        try:
                                            text_exp = int(re.findall(r'\d+', text)[0])
                                            details_exp = int(re.findall(r'\d+', text)[0])
                                            text = text.replace(str(text_exp), f"{text_exp:,}")
                                            details = details.replace(str(details_exp), f"{details_exp:,}")
                                        except IndexError:
                                            pass
                                        embed = discord.Embed(title=text, description=details)
                                        embed.set_author(name=player, icon_url=icon_url)
                                        embed.set_thumbnail(url=banner)
                                        embed.set_footer(text=activity.get('date'))
                                        try:
                                            await channel.send(embed=embed)
                                        except Exception as e:
                                            tb = traceback.format_exc()
                                            print(e, tb)

                        print(f"Finished sending adv log data for clan {get_clan.get('name')}")
                    print(f"Sent adv. log data at {datetime.datetime.utcnow()}. Sleeping for 10 minutes.")
                    await asyncio.sleep(60 * 10)
            except Exception as e:
                print(f'{e}: {traceback.format_exc()}')

    @staticmethod
    async def retrieve_clan_list(cs: aiohttp.ClientSession, clan_name: str) -> list:
        clan_name = clan_name.replace(' ', '%20')
        clan = f"http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName={clan_name}"
        async with cs.get(clan) as r:
            clan_csv = await r.text()
            return list(csv.reader(StringIO(clan_csv), delimiter=','))

    # @staticmethod
    # async def retrieve_activities(cs: aiohttp.ClientSession, player_name: str) -> list:
    #     player_name = player_name.replace(' ', '%20')
    #     profile_url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player_name}&activities=20'
    #     async with cs.get(profile_url) as r:
    #         if r.status != 200:
    #             return []
    #         call = await r.json()
    #         if call.get('error') == 'PROFILE_PRIVATE':
    #             return []
    #         elif call.get('error') == 'NOT_A_MEMBER':
    #             return []
    #         else:
    #             if call.get('activities'):
    #                 return ast.literal_eval(str(call.get('activities')))
    #             return []


def setup(bot):
    bot.add_cog(AdvLog(bot))
