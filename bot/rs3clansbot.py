#!/usr/bin/env python3

# Standard lib imports
import asyncio
import configparser
import datetime
import logging
from pathlib import Path

# Non-Standard lib imports
# import discord
from discord.ext import commands

# Local imports
from definesettings import file_exists, generate_settings

if file_exists("bot_settings.ini"):
    print("Existing Settings found, reading them...")
    config_file = configparser.ConfigParser()
    config_file.read("bot_settings.ini")
    BOT_TOKEN = config_file['DISCORD']['bot_token']
    OAUTH_URL = config_file['DISCORD']['oauth_url']
    PLAYING_NOW = config_file['DISCORD']['playing_now']
    PREFIX = config_file['DISCORD']['commands_prefix']
    DESCRIPTION = config_file['DISCORD']['bot_description']
    LANGUAGE = config_file['DISCORD']['language']
    CLAN_NAME = config_file['RUNESCAPE']['clan_name']
else:
    answer = input("Settings not found. Do you wish the re-create them? (y/N)\n\n>> ")
    if answer is 'y' or answer is 'Y':
        generate_settings()
        config_file = configparser.ConfigParser()
        config_file.read("bot_settings.ini")
        BOT_TOKEN = config_file['DISCORD']['bot_token']
        OAUTH_URL = config_file['DISCORD']['oauth_url']
        PLAYING_NOW = config_file['DISCORD']['playing_now']
        PREFIX = config_file['DISCORD']['commands_prefix']
        DESCRIPTION = config_file['DISCORD']['bot_description']
        LANGUAGE = config_file['DISCORD']['language']
        CLAN_NAME = config_file['RUNESCAPE']['clan_name']
    else:
        raise KeyError("Couldn't read settings. Verify if 'bot_settings.ini' exists and is correctly configured.")


async def run():
    bot = Bot(description=DESCRIPTION)
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()


class Bot(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=PREFIX,
            description=kwargs.pop('description')
        )
        self.start_time = None
        self.app_info = None
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_all_extensions(self):
        """
        Attempts to load all .py files in /cogs/ as cog extensions
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'- loaded Extension: {extension}')
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
        print(f"Bot logged on as '{self.user.name}'\n"
              f"Owner: '{self.app_info.owner}'\n"
              f"ID: '{self.user.id}'\n"
              f"Oauth URL: '{OAUTH_URL}'\n\n"
              f"[ Bot Settings ]\n"
              f"- Clan Name: '{CLAN_NAME}'\n"
              f"- Playing Message: '{PLAYING_NOW}'\n"
              f"- Commands prefix: '{PREFIX}'\n")

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        if message.author.bot:
            return  # ignore all bots
        await self.process_commands(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
