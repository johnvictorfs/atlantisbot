#!/usr/bin/env python3

# Standard lib imports
import asyncio
import logging
import datetime
import re
from pathlib import Path

# Non-Standard lib imports
import discord
from discord.ext import commands

# Local imports
import definesettings as setting


async def run():
    bot = Bot(description=setting.DESCRIPTION)
    try:
        await bot.start(setting.BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()


def raids_embed():
    embed_title = "**Raids**"

    clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{setting.CLAN_NAME}/clanmotif.png"
    raids_notif_embed = discord.Embed(title=embed_title,
                                      description="",
                                      color=discord.Colour.dark_blue())
    raids_notif_embed.set_thumbnail(url=clan_banner_url)

    raids_notif_embed.add_field(
        name="Marque presença para os Raids de 21:00",
        value=f"{setting.RAIDS_CHAT_ID}\n"
              f"\n"
              f"É obrigatório ter a tag <@&376410304277512192>\n    - Leia os tópicos fixos para saber como obter\n"
              f"\n"
              f"Não mande mensagens desnecessárias no {setting.RAIDS_CHAT_ID}\n"
              f"\n"
              f"Não marque presença mais de uma vez\n"
              f"\n"
              f"Esteja online no jogo no mundo 75 até 20:50 em ponto.\n"
              f"- Risco de remoção do time caso contrário. Não cause atrasos",
        inline=False)
    return raids_notif_embed


async def raids_notification(user, channel, start_day, channel_public=None, time_to_send="23:00:00"):
    while True:
        today = datetime.datetime.utcnow().date()
        if (today - start_day).days % 2 == 0:
            date = str(datetime.datetime.utcnow().time())
            time = date[0:7]
            time_to_send = time_to_send[0:7]
            if time == time_to_send:
                team_list = []
                embed = raids_embed()
                print(f"Sent Raids notification, time: {time}")
                await channel.send(content="<@&376410304277512192>", embed=embed)
                raids_notif_msg = await channel.history().get(author=user)
                team_embed = discord.Embed(
                    title="__Time Raids__",
                    description=""
                )
                await channel.send(embed=team_embed)
                raids_team_message = await channel.history().get(author=user)
                await channel_public.send(
                    content=f"--- Presenças para os Raids das 21:00 serão contadas a partir dessa mensagem ---\n\n"
                            f"Marque presença apenas se for estar **online** no jogo até 20:50 "
                            f"em ponto **no Mundo 75.**\n\n"
                            f"`in`: Marcar presença\n"
                            f"`out`: Retirar presença")
                last_message = await channel_public.history().get(author=user)
                sent_time = datetime.datetime.now()
                while True:
                    async for message in channel_public.history(after=last_message):
                        if message.content.lower() == 'in':
                            if len(team_list) >= 10:
                                await channel_public.send(f"O time de Raids já está cheio!")
                            else:
                                if 'Raids' in str(message.author.roles):
                                    if message.author.mention in team_list:
                                        await channel_public.send(f"Ei {message.author.mention}, você já está no time! Não tente me enganar.")
                                    else:
                                        await channel_public.send(f"{message.author.mention} adicionado ao time de Raids.")
                                        team_list.append(message.author.mention)
                                else:
                                    await channel_public.send(f"{message.author.mention}, você não tem permissão para ir Raids ainda. Aplique agora usando o comando `{setting.PREFIX}raids`!")
                        if message.content.lower() == 'out':
                            if message.author.mention in team_list:
                                team_list.remove(message.author.mention)
                                await channel_public.send(f"{message.author.mention} foi removido do time de Raids.")
                            else:
                                await channel_public.send(f"Ei {message.author.mention}, você já não estava no time! Não tente me enganar.")
                        last_message = message
                    team_embed = discord.Embed(
                        title="__Time Raids__",
                        description=""
                    )
                    i = 1
                    for person in team_list:
                        team_embed.add_field(
                            name=("_\\" * 15) + "_",
                            value=f"{i}- {person}",
                            inline=False
                        )
                        i += 1
                    await raids_team_message.edit(embed=team_embed)
                    diff = datetime.datetime.now() - sent_time
                    if diff.total_seconds() > (60 * 120):
                        break
                await asyncio.sleep(60 * 5)
                await raids_notif_msg.delete()
                await raids_team_message.delete()
        await asyncio.sleep(5)


class Bot(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=setting.PREFIX,
            description=kwargs.pop('description'),
            case_insensitive=True,
        )
        self.remove_command('help')
        self.start_time = None
        self.app_info = None
        self.raids_channel = None
        self.raids_channel_public = None
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out up-time.
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)
        if 'raids_notif' not in setting.DISABLED_COGS:
            if setting.ATLBOT_ENV == 'prod':
                self.raids_channel = self.get_channel(393104367471034369)
                self.raids_channel_public = self.get_channel(393696030505435136)
            elif setting.ATLBOT_ENV == 'dev':
                self.raids_channel = self.get_channel(505240114662998027)
                self.raids_channel_public = self.get_channel(505240135390986262)
            raids_start_day = datetime.date(2018, 10, 25)
            raids_time = "23:00:00"
            print(f"-- Channel set to send raids notification: #{self.raids_channel} at {raids_time}")
            print(f"-- Channel set to send raids presence notifications: #{self.raids_channel_public}")
            self.loop.create_task(raids_notification(
                user=self.user,
                channel=self.raids_channel,
                start_day=raids_start_day,
                channel_public=self.raids_channel_public,
                time_to_send=raids_time))
        self.start_time = datetime.datetime.utcnow()

    async def load_all_extensions(self):
        """
        Attempts to load all .py files in /cogs/ as cog extensions
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing

        if setting.ATLBOT_ENV == 'prod':
            cogs = ['chat', 'clan', 'competitions', 'error_handler', 'raids_day', 'rsatlantis', 'welcome_message']
        else:
            cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            if extension not in setting.DISABLED_COGS:
                try:
                    self.load_extension(f'cogs.{extension}')
                    print(f'- loaded Extension: {extension}')
                except discord.ClientException:
                    pass
                except Exception as e:
                    error = f'{extension}\n {type(e).__name__} : {e}'
                    print(f'failed to load extension {error}')
        print('-' * 10)

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        await self.change_presence(game=discord.Game(name=setting.PLAYING_NOW))
        print(f"Bot logged on as '{self.user.name}'\n"
              f"Owner: '{self.app_info.owner}'\n"
              f"ID: '{self.user.id}'\n"
              f"Oauth URL: '{setting.OAUTH_URL}'\n\n"
              f"[ Bot Settings ]\n"
              f"- Clan Name: '{setting.CLAN_NAME}'\n"
              f"- Playing Message: '{setting.PLAYING_NOW}'\n"
              f"- Commands prefix: '{setting.PREFIX}'\n"
              f"- Language: '{setting.LANGUAGE}'\n"
              f"- Show titles on claninfo: '{setting.SHOW_TITLES}'")

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        if message.author.bot:
            return

        # Replace old Rs Wikia links to the new Rs Wiki links
        if 'http' in message.content and 'runescape.wikia.com/wiki/' in message.content:
            urls = re.findall(r"http\S+", message.content)

            formatted_urls = []
            for url in urls:
                if 'runescape.wikia.com/wiki/' in url:
                    url = url.replace('runescape.wikia.com/wiki/', 'runescape.wiki/w/')
                    formatted_urls.append(url)

            formatted_urls_string = ''
            for url in formatted_urls:
                formatted_urls_string += f'- ***<{url}>***\n\n'

            await message.channel.send(f'Olá, parece que você usou um ou mais links para a antiga Wiki do RuneScape!'
                                       f'\n\n'
                                       f'Recentemente a Jagex, com ajuda dos Admins da wiki, '
                                       f'passou a hostear a wiki do jogo em seu próprio site, ao '
                                       f'invés do[s] link[s] que você enviou, utilize o[s] link[s] abaixo:\n\n'
                                       f'{formatted_urls_string}'
                                       f'Ajude-nos a fazer a nova wiki ser conhecida por todos :)')

        await self.process_commands(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
