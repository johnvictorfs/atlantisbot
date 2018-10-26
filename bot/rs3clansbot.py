#!/usr/bin/env python3

# Standard lib imports
import asyncio
import logging
import datetime
import re
import os
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


def raids_embed(ntype='fr'):
    if ntype == 'fr':
        embed_title = "**Raids**"
    else:
        embed_title = "**Durzag**"

    clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{setting.CLAN_NAME}/clanmotif.png"
    raids_notif_embed = discord.Embed(title=embed_title,
                                      description="",
                                      color=discord.Colour.dark_blue())
    raids_notif_embed.set_thumbnail(url=clan_banner_url)

    if ntype == 'fr':
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
    else:
        raids_notif_embed.add_field(
            name="Marque presença para o Durzag de 19:00",
            value=f"{setting.RAIDS_CHAT_ID}\n"
                  f"\n"
                  f"Para obter a tag <@&488121068834258954> reaja ao ícone <:durzag:488178236774154240>"
                  f" no canal <#382691780996497416>\n"
                  f"\n"
                  f"Não mande mensagens desnecessárias no {setting.RAIDS_CHAT_ID}\n"
                  f"\n"
                  f"Não marque presença mais de uma vez\n",
            inline=False)

    return raids_notif_embed


async def bm_notification(channel, channel_public=None, time_to_send="18:00:0"):
    while True:
        dia_raids = os.environ.get('RAIDS_DAY', 1)
        current_day = datetime.datetime.utcnow().day
        if int(current_day) % 2 == 0:
            # O dia aqui tem que ser o contrário do dia de Raids normal, já que eles são alternados
            current_day = 'impar'
        else:
            current_day = 'par'

        date = str(datetime.datetime.utcnow().time())
        time = date[0:7]
        time_to_send = time_to_send[0:7]

        if time == time_to_send and current_day == dia_raids:
            embed = raids_embed(ntype="bm")
            print(f"Sent Raids notification, time: {time} - Dia: {current_day}({dia_raids})")
            if channel_public:
                await channel_public.send(content="--- Presenças serão contadas a partir dessa mensagem ---\n\n"
                                                  "Marque presença para o BM Durzag das 19:00.")
            await channel.send(content="<@&488121068834258954>", embed=embed)
            await asyncio.sleep(60)
        await asyncio.sleep(5)


async def raids_notification(channel, channel_public=None, time_to_send="20:00:0"):
    while True:
        dia_raids = os.environ.get('RAIDS_DAY', 1)
        current_day = datetime.datetime.utcnow().day
        if int(current_day) % 2 == 0:
            current_day = 'par'
        else:
            current_day = 'impar'

        date = str(datetime.datetime.utcnow().time())
        time = date[0:7]
        time_to_send = time_to_send[0:7]
        if time == time_to_send and current_day == dia_raids:
            embed = raids_embed()
            print(f"Sent Raids notification, time: {time} - Dia: {current_day}({dia_raids})")
            if channel_public:
                await channel_public.send(content="--- Presenças serão contadas a partir dessa mensagem ---\n\n"
                                                  "Marque presença apenas se for estar online no jogo até 20:50 "
                                                  "em ponto no Mundo 75.")
            await channel.send(content="<@&376410304277512192>", embed=embed)
            await asyncio.sleep(60)
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
        self.bm_channel = None
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
        if 'raids_day' not in setting.DISABLED_COGS:
            # self.raids_channel = self.get_channel(393104367471034369)
            self.raids_channel = self.get_channel(450059325810016267)

            self.bm_channel = self.get_channel(488112229430984704)
            # self.raids_channel_public = self.get_channel(393696030505435136)
            self.raids_channel_public = self.get_channel(450059325810016267)

            bm_time = "18:00:00"
            raids_time = "02:43:00"
            # print(f"-- Channel set to send bm notification: #{self.bm_channel} at {bm_time}")
            print(f"-- Channel set to send raids notification: #{self.raids_channel} at {raids_time}")
            print(f"-- Channel set to send public notifications: #{self.raids_channel_public}")
            self.loop.create_task(raids_notification(
                channel=self.raids_channel,
                channel_public=self.raids_channel_public,
                time_to_send=raids_time))
            # self.loop.create_task(bm_notification(
            # channel=self.bm_channel,
            # channel_public=self.raids_channel_public,
            # time_to_send=bm_time))
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
