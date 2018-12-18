#!/usr/bin/env python3

import asyncio
import logging
import datetime
import os
import re
import sys
import json
from pathlib import Path

import colorama
import discord
from discord.ext import commands

from bot import settings
from bot.tasks.advlog import advlog
from bot.tasks.raids import raids_notification
from bot.tasks.pvmteams import team_maker
from bot.utils.tools import separator, has_any_role


async def run():
    bot = Bot()
    try:
        await bot.start(bot.setting.token)
    except KeyboardInterrupt:
        print(f"{colorama.Fore.RED}KeyBoardInterrupt. Logging out...")
        await bot.logout()
    except discord.errors.LoginFailure:
        print(f"{colorama.Fore.RED}Error: Invalid Token. Please input a valid token in '/bot/bot_settings.json' file.")
        sys.exit(1)


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=self.setting.prefix, description=self.setting.description, case_insensitive=True)
        self.remove_command('help')
        self.start_time = None
        self.app_info = None
        self.raids_channel = None
        self.raids_channel_public = None
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def send_logs(self, e, tb, ctx: commands.Context = None):
        dev = self.get_user(self.setting.developer_id)
        if ctx:
            info_embed = discord.Embed(title="__Error Info__", color=discord.Color.dark_red())
            info_embed.add_field(name="Message", value=ctx.message.content, inline=False)
            info_embed.add_field(name="By", value=ctx.author, inline=False)
            info_embed.add_field(name="In Guild", value=ctx.guild, inline=False)
            info_embed.add_field(name="In Channel", value=ctx.channel, inline=False)
            await dev.send(embed=info_embed)
        try:
            await dev.send(f"{separator}\n**{e}:**\n```python\n{tb}```")
        except discord.errors.HTTPException:
            print(f"{e}: {tb}")
            await dev.send(f"(Sending first 500 chars of traceback, too long)\n{separator}\n**{e}:**"
                           f"\n```python\n{tb[:500]}```")

    @property
    def setting(self):
        try:
            with open('bot/bot_settings.json', 'r'):
                return settings.Settings()
        except FileNotFoundError:
            with open('bot/bot_settings.json', 'w') as f:
                json.dump(settings.default_settings, f, indent=4)
                if not os.environ.get('ATLBOT_TOKEN'):
                    print(f"{colorama.Fore.YELLOW}Settings not found. Default settings file created. "
                          "Edit '/bot/bot_settings.json' to change settings, then reload the bot.")
                    sys.exit(1)
                else:
                    with open('bot/bot_settings.json', 'w') as heroku_settings:
                        json.dump(settings.default_settings, heroku_settings, indent=4)
                        return settings.Settings()

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out up-time.
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)
        self.start_time = datetime.datetime.utcnow()

    @staticmethod
    def get_cogs():
        """Gets cog names from /cogs/ folder"""
        not_extensions = ['utils', 'embeds', 'models', '__init__']
        cogs = [x.stem for x in Path('bot/cogs').glob('*.py')]
        for cog in cogs:
            if cog in not_extensions:
                cogs.remove(cog)
        return cogs

    async def unload_all_extensions(self):
        """Unloads all cog extensions"""
        errored = False
        for extension in self.get_cogs():
            if extension not in self.setting.disabled_extensions:
                try:
                    self.unload_extension(f'bot.cogs.{extension}')
                    print(f'- Unloaded extension {extension}')
                except Exception as e:
                    error = f'{extension}:\n {type(e).__name__} : {e}'
                    print(f'Failed to unload extension {error}')
                    errored = True
        return errored

    async def load_all_extensions(self):
        """Attempts to load all .py files in /cogs/ as cog extensions"""
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        errored = False
        for extension in self.get_cogs():
            if extension not in self.setting.disabled_extensions:
                try:
                    self.load_extension(f'bot.cogs.{extension}')
                    print(f'- loaded Extension: {extension}')
                except Exception as e:
                    error = f'{extension}:\n {type(e).__name__} : {e}'
                    print(f'Failed to load extension {error}')
                    errored = True
        print('-' * 10)
        return errored

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        await self.change_presence(activity=discord.Game(name=self.setting.playing_message))
        print(f"Bot logged on as '{self.user.name}'\n"
              f"Mode: {self.setting.mode}\n"
              f"Argvs: {sys.argv}\n"
              f"Owner: '{self.app_info.owner}'\n"
              f"ID: '{self.user.id}'\n"
              f"[ Bot Settings ]\n"
              f"- Clan Name: '{self.setting.clan_name}'\n"
              f"- Playing Message: '{self.setting.playing_message}'\n"
              f"- Commands prefix: '{self.setting.prefix}'\n"
              f"- Show titles on claninfo: '{self.setting.show_titles}'")
        if self.setting.mode == 'prod':
            self.raids_channel = self.get_channel(self.setting.chat.get('raids'))
            self.raids_channel_public = self.get_channel(self.setting.chat.get('raids_chat'))
        elif self.setting.mode == 'dev':
            self.raids_channel = self.get_channel(505240114662998027)
            self.raids_channel_public = self.get_channel(505240135390986262)
        raids_start_day = datetime.datetime.strptime(self.setting.raids_start_date, "%Y/%m/%d").date()
        raids_time = self.setting.raids_time_utc
        print(f"-- Channel set to send raids notification: #{self.raids_channel} at {raids_time}")
        print(f"-- Channel set to send raids presence notifications: #{self.raids_channel_public}")
        self.loop.create_task(raids_notification(
            setting=self.setting,
            user=self.user,
            channel=self.raids_channel,
            start_day=raids_start_day,
            channel_public=self.raids_channel_public,
            time_to_send=raids_time))
        self.loop.create_task(team_maker(self))
        self.loop.create_task(advlog(self))

    async def on_message(self, message: discord.Message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        if message.author.bot:
            if message.content == 'HECK YES!':
                return await message.channel.send('HECK NO!')
            return

        # If in development environment only accept answers in dev server and channel
        if self.setting.mode == 'dev':
            if not message.guild:
                if message.author.id != self.setting.developer_id:
                    return
            elif message.guild.id != self.setting.dev_guild and message.channel.id != 488106800655106058:
                return

        membro = self.setting.role.get('membro')
        convidado = self.setting.role.get('convidado')
        unauthorized_mentions = ['@everyone', '@here', f"<@&{membro}>", f"<@&{convidado}>"]
        if any(mention in message.content for mention in unauthorized_mentions):
            if has_any_role(message.author, membro, convidado):
                embed = discord.Embed(
                    title="__Quebra de Conduta__",
                    description=separator,
                    color=discord.Color.dark_red(),
                )
                embed.add_field(
                    name=f"Por favor não utilize as seguintes menções sem permissão para tal:",
                    value=f"<@&{membro}> - <@&{convidado}> - @everyone - @here",
                    inline=False
                )
                embed.set_author(
                    name="Administração",
                    icon_url="http://www.runeclan.com/images/ranks/1.png"
                )
                embed.set_thumbnail(
                    url=f"http://services.runescape.com/m=avatar-rs/{self.setting.clan_name}/clanmotif.png"
                )
                embed.set_footer(
                    text="Nosso servidor abriga uma quantidade muito grande de pessoas, "
                         "tenha bom senso ao utilizar uma menção que irá notificar centenas de pessoas."
                )
                print(f'> {message.author} used a not allowed mention '
                      f'in channel #{message.channel} at {datetime.datetime.now()}')
                print(f"Content:\n<\n{message.content}\n>")
                await message.delete()
                return await message.channel.send(content=message.author.mention, embed=embed)

        # Replace old Rs Wikia links to the new Rs Wiki links
        if 'http' in message.content and 'runescape.fandom.com/wiki' in message.content:
            urls = re.findall(r"http\S+", message.content)
            formatted_urls = []
            for url in urls:
                if 'runescape.fandom.com/wiki' in url:
                    url = url.replace('runescape.fandom.com/wiki', 'runescape.wiki/w/')
                    formatted_urls.append(url)

            formatted_urls_string = ''
            for url in formatted_urls:
                formatted_urls_string += f'- ***<{url}>***\n\n'
            plural = ''
            if len(formatted_urls) > 1:
                plural = 's'
            await message.channel.send(
                f'Olá, parece que você usou um ou mais links para a antiga Wiki do RuneScape!'
                f'\n\n'
                f'Recentemente os Admins da Wiki, com ajuda da Jagex, '
                f'passou a hostear a wiki do jogo no site oficial do RuneScape, ao '
                f'invés do{plural} link{plural} que você enviou, utilize o{plural} link{plural} abaixo:\n\n'
                f'{formatted_urls_string}'
                f'Ajude-nos a fazer a nova wiki ser conhecida por todos :)')
        await self.process_commands(message)


if __name__ == '__main__':
    colorama.init()
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
