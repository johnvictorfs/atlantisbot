#!/usr/bin/env python3

# Standard lib imports
import asyncio
import datetime
import logging
import datetime
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


async def raids_embed():

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
              f"É obrigatório ter a tag <@&376410304277512192> - Leia os tópicos fixos para saber como obter\n"
              f"\n"
              f"Não mande mensagens desnecessárias no {setting.RAIDS_CHAT_ID}\n"
              f"\n"
              f"Não marque presença mais de uma vez",
        inline=False)

    return raids_notif_embed


async def raids_notification(channel, time_to_send="20:00"):
    while True:
        date = str(datetime.datetime.now().time())
        time = date[0] + date[1] + date[2] + date[3] + date[4]

        if time == time_to_send:
            embed = raids_embed()
            print(f"Sent raids notification, time: {date}")
            await channel.send("<@&376410304277512192>")
            await channel.send(embed=embed)

        await asyncio.sleep(60)


class Bot(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=setting.PREFIX,
            description=kwargs.pop('description'),
        )
        self.start_time = None
        self.app_info = None
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.loop.create_task(raids_notification(channel=self.get_channel(450059325810016267)))

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out up-time.
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
        print('-' * 10)
        for extension in cogs:
            # noinspection PyBroadException
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
            return  # ignore all bots
        await self.process_commands(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
