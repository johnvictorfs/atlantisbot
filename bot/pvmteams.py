import asyncio
import json
import traceback
import os

import discord

from .cogs.utils import has_role, separator

"""
1. Every 1 second check every team in pvm_teams.json
2. Check the respective channels for new entries
3. Check all entries/leaves in the history after the invite message
4. Delete all entries/leaves messages, so they don't get checked on the next loop
5. Add/remove the respective people from the team only from valid entries/leaves
6. Send a message in the channel saying who was Added/removed
7. Update the Json File
"""


async def team_maker(client):
    while True:
        try:
            with open('pvm_teams.json', 'r') as f:
                current_teams = json.load(f)
            # Iterating through a copy of the list instead of the actual list of teams.
            # That way i can safely remove items inside the original list, so i can
            # update it later.
            for team in current_teams.get('teams')[:]:
                invite_channel = client.get_channel(team['invite_channel_id'])
                team_channel = client.get_channel(team['team_channel_id'])
                try:
                    invite_message = await invite_channel.get_message(team['invite_message_id'])
                except discord.errors.NotFound:
                    with open('pvm_teams.json', 'w') as f:
                        current_teams['teams'].remove(team)
                        json.dump(current_teams, f, indent=2)
                    continue
                try:
                    team_message = await team_channel.get_message(team['team_message_id'])
                except discord.errors.NotFound:
                    with open('pvm_teams.json', 'w') as f:
                        current_teams['teams'].remove(team)
                        json.dump(current_teams, f, indent=2)
                    continue
                async for message in team_channel.history(after=team_message):
                    if message.content.lower() == f"{client.setting.prefix}del {team['id']}":
                        allowed_roles = ['mod', 'mod+', 'admin']
                        if (any([has_role(message.author, client.setting.role.get(role)) for role in allowed_roles])
                                or message.author.id == team['author_id']):
                            await message.delete()
                            try:
                                await invite_message.delete()
                            except discord.errors.NotFound:
                                pass
                            try:
                                await team_message.delete()
                            except discord.errors.NotFound:
                                pass
                            for message_id in team['bot_messages']:
                                try:
                                    message = await invite_channel.get_message(message_id)
                                    await message.delete()
                                except Exception:
                                    pass
                            with open('pvm_teams.json', 'w') as f:
                                current_teams['teams'].remove(team)
                                json.dump(current_teams, f, indent=2)
                            try:
                                await message.author.send(f"Time '{team['title']}' excluído com sucesso.")
                            except discord.errors.HTTPException:
                                pass
                            continue
                async for message in invite_channel.history(after=invite_message):
                    if message.content.lower() == f"{client.setting.prefix}del {team['id']}":
                        allowed_roles = ['mod', 'mod+', 'admin']
                        if (any([has_role(message.author, client.setting.role.get(role)) for role in allowed_roles])
                                or message.author.id == team['author_id']):
                            await message.delete()
                            try:
                                await invite_message.delete()
                            except discord.errors.NotFound:
                                pass
                            try:
                                await team_message.delete()
                            except discord.errors.NotFound:
                                pass
                            for message_id in team['bot_messages']:
                                try:
                                    message = await invite_channel.get_message(message_id)
                                    await message.delete()
                                except Exception:
                                    pass
                            with open('pvm_teams.json', 'w') as f:
                                current_teams['teams'].remove(team)
                                json.dump(current_teams, f, indent=2)
                            try:
                                await message.author.send(f"Time '{team['title']}' excluído com sucesso.")
                            except discord.errors.HTTPException:
                                pass
                            continue
                    elif message.content.lower() == f"in {team['id']}":
                        await message.delete()
                        if message.author.bot:
                            continue
                        if has_role(message.author, team['role']) or not team['role']:
                            if len(team['players']) < team['size']:
                                if message.author.mention not in team['players']:
                                    team['players'].append(message.author.mention)
                                    message = await invite_channel.send(
                                        f"{message.author.mention} foi adicionado ao Time '{team['title']}'\n"
                                        f"*(`in {team['id']}`)*"
                                    )
                                    team['bot_messages'].append(message.id)
                                else:
                                    message = await invite_channel.send(
                                        f"{message.author.mention}, você já está no Time '{team['title']}'\n"
                                        f"*(`in {team['id']}`)*"
                                    )
                                    team['bot_messages'].append(message.id)
                            else:
                                message = await invite_channel.send(
                                    f"{message.author.mention}, o Time '{team['title']}' já está cheio.\n"
                                    f"*(`in {team['id']}`)*"
                                )
                                team['bot_messages'].append(message.id)
                        else:
                            no_perm_embed = discord.Embed(
                                title=f"__Permissões insuficientes__",
                                description=f"{message.author.mention}, você precisa ter o cargo <@&{team['role']}> "
                                            f"para entrar no Time '{team['title']}'"
                                            f"\n(*`in {team['id']}`*)",
                                color=discord.Color.dark_red()
                            )
                            message = await invite_channel.send(embed=no_perm_embed)
                            team['bot_messages'].append(message.id)
                    elif message.content.lower() == f"out {team['id']}":
                        await message.delete()
                        if message.author.bot:
                            continue
                        if message.author.mention in team['players']:
                            team['players'].remove(message.author.mention)
                            message = await invite_channel.send(
                                f"{message.author.mention} foi removido do Time '{team['title']}'\n"
                                f"*(`in {team['id']}`)*"
                            )
                            team['bot_messages'].append(message.id)
                        else:
                            message = await invite_channel.send(
                                f"{message.author.mention}, você já não está no time '{team['title']}'!.\n"
                                f"*(`out {team['id']}`)*"
                            )
                            team['bot_messages'].append(message.id)
                # Updating the team message with the all the removals/added people
                description = f"Marque presença no <#{team['invite_channel_id']}>"
                if team['role']:
                    description = f"Requisito: <@&{team['role']}>\n{description}"
                team_embed = discord.Embed(
                    title=f"__{team['title']}__ - {len(team['players'])}/{team['size']}",
                    description=description,
                    color=discord.Color.purple()
                )
                footer = (f"Digite '{client.setting.prefix}del {team['id']}' "
                          f"para excluir o time. (Criador do time ou Mod+)")
                team_embed.set_footer(
                    text=footer
                )
                for index, member in enumerate(team['players']):
                    team_embed.add_field(
                        name=separator,
                        value=f"{index + 1}- {member}",
                        inline=False
                    )
                try:
                    await team_message.edit(embed=team_embed)
                except discord.errors.NotFound:
                    continue
                with open('pvm_teams.json', 'w') as f:
                    json.dump(current_teams, f, indent=2)
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            pass
        except Exception as e:
            tb = traceback.format_exc()
            print(f"{e}: {tb}")
        await asyncio.sleep(1)
