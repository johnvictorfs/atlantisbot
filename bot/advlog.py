import asyncio
import csv
import traceback
import re
import ast
import datetime
from io import StringIO

import aiohttp
import discord

from .cogs.models import Session, PlayerActivities


async def advlog(client):
    while True:
        async with aiohttp.ClientSession() as cs:
            clan = f"http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName={client.setting.clan_name}"
            async with cs.get(clan) as r:
                clan_csv = await r.text()
                clan_list = list(csv.reader(StringIO(clan_csv), delimiter=','))
            new_activities = {}
            success = 0
            profile_private = 0
            not_member = 0
            print(f"Started checking for new adventurer's log entries from clanmates at {datetime.datetime.utcnow()}.")
            for player in clan_list[1:]:
                player = player[0]
                profile_url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player}&activities=20'
                async with cs.get(profile_url) as r:
                    call = await r.json()
                    if call.get('error') == 'PROFILE_PRIVATE':
                        new_activities[player] = []
                        profile_private += 1
                    elif call.get('error') == 'NOT_A_MEMBER':
                        new_activities[player] = []
                        not_member += 1
                    else:
                        if call.get('activities'):
                            # TODO: Since this list can't be .reversed(), sort the dictionaries inside them by date
                            new_activities[player] = ast.literal_eval(str(call.get('activities')))
                            success += 1
            print(f"Finished grabbing adv log data. Success: {success} "
                  f"- Private Profile: {profile_private} "
                  f"- Not a Member: {not_member}")
            session = Session()
            all_activities = session.query(PlayerActivities).all()
            old_activities = {}
            if all_activities:
                for act in all_activities:
                    act_list = ast.literal_eval(act.activities)
                    old_activities[act.name] = act_list
            new_keys = set(new_activities) - set(old_activities)
            difference = {}
            for key, item in new_activities.items():
                if key not in new_keys:
                    diff_items = []
                    if item:
                        if old_activities.get(key):
                            diff_items = [act for act in item if act not in old_activities.get(key)]
                        else:
                            diff_items = [act for act in item]
                    difference[key] = diff_items
            difference.update({k: new_activities[k] for k in new_keys})
            for key, item in new_activities.items():
                old_player = session.query(PlayerActivities).filter_by(name=key).first()
                if old_player:
                    old_player.activities = str(item)
                else:
                    new_player = PlayerActivities(name=key, activities=str(item))
                    session.add(new_player)
                session.commit()
            session.close()
            channel = client.get_channel(client.setting.chat.get('adv_log'))
            banner = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{client.setting.clan_name}/clanmotif.png"
            for player, activities in difference.items():
                player_name = player.replace(' ', '%20').replace('%C2%A0', '%20')
                icon_url = f"https://secure.runescape.com/m=avatar-rs/{player_name}/chat.png"
                if activities:
                    for activity in activities:
                        text = activity.get('text')
                        details = activity.get('details')
                        try:
                            text_exp = int(re.findall('\d+', text)[0])
                            details_exp = int(re.findall('\d+', text)[0])
                            text = text.replace(str(text_exp), f"{text_exp:,}")
                            details = details.replace(str(details_exp), f"{details_exp:,}")
                        except IndexError:
                            pass
                        embed = discord.Embed(
                            title=text,
                            description=details
                        )
                        embed.set_author(
                            name=player,
                            icon_url=icon_url
                        )
                        embed.set_thumbnail(url=banner)
                        embed.set_footer(text=activity.get('date'))
                        try:
                            await channel.send(embed=embed)
                        except Exception as e:
                            tb = traceback.format_exc()
                            print(e, tb)
        print(f"Sent adv. log data at {datetime.datetime.utcnow()}. Sleeping for 10 minutes.")
        await asyncio.sleep(60 * 10)


a = [
    {
        'date': '19-Nov-2018 09:04',
        'details': 'I now have at least 72000000 experience points in the Summoning skill.',
        'text': '72000000XP in Summoning'
    },
    {
        'date': '19-Nov-2018 08:32',
        'details': 'I now have at least 70000000 experience points in the Summoning skill.',
        'text': '70000000XP in Summoning'
    },
    {
        'date': '19-Nov-2018 08:09',
        'details': 'I now have at least 150000000 experience points in the Dungeoneering skill.',
        'text': '150000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 07:38',
        'details': 'I now have at least 148000000 experience points in the Dungeoneering skill.',
        'text': '148000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 06:45',
        'details': 'I now have at least 146000000 experience points in the Dungeoneering skill.',
        'text': '146000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 06:00',
        'details': 'I now have at least 144000000 experience points in the Dungeoneering skill.',
        'text': '144000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 05:30',
        'details': 'I now have at least 142000000 experience points in the Dungeoneering skill.',
        'text': '142000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 04:49',
        'details': 'I now have at least 140000000 experience points in the Dungeoneering skill.',
        'text': '140000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 03:57',
        'details': 'I now have at least 138000000 experience points in the Dungeoneering skill.',
        'text': '138000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 03:26',
        'details': 'I now have at least 136000000 experience points in the Dungeoneering skill.',
        'text': '136000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 02:32',
        'details': 'I now have at least 134000000 experience points in the Dungeoneering skill.',
        'text': '134000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 01:43',
        'details': 'I now have at least 132000000 experience points in the Dungeoneering skill.',
        'text': '132000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 00:58',
        'details': 'I now have at least 130000000 experience points in the Dungeoneering skill.',
        'text': '130000000XP in Dungeoneering'
    },
    {
        'date': '19-Nov-2018 00:17',
        'details': 'I now have at least 128000000 experience points in the Dungeoneering skill.',
        'text': '128000000XP in Dungeoneering'
    },
    {
        'date': '18-Nov-2018 23:50',
        'details': 'I now have at least 126000000 experience points in the Dungeoneering skill.',
        'text': '126000000XP in Dungeoneering'
    },
    {
        'date': '18-Nov-2018 22:41',
        'details': 'I now have at least 124000000 experience points in the Dungeoneering skill.',
        'text': '124000000XP in Dungeoneering'
    },
    {
        'date': '18-Nov-2018 20:48',
        'details': 'I now have at least 68000000 experience points in the Summoning skill.',
        'text': '68000000XP in Summoning'
    },
    {
        'date': '18-Nov-2018 19:23',
        'details': 'I now have at least 66000000 experience points in the Summoning skill.',
        'text': '66000000XP in Summoning'
    },
    {
        'date': '18-Nov-2018 18:31',
        'details': 'I now have at least 64000000 experience points in the Summoning skill.',
        'text': '64000000XP in Summoning'
    },
    {
        'date': '18-Nov-2018 17:14',
        'details': 'I now have at least 62000000 experience points in the Summoning skill.',
        'text': '62000000XP in Summoning'
    }
]
