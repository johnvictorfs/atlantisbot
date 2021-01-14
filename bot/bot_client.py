import asyncio
import logging
import datetime
import traceback
import re
import sys
import json
import aiohttp
from pathlib import Path
from pprint import pformat
from typing import Optional, Dict, Any

import colorama
import twitter
import discord
from discord.ext import commands
from atlantisbot_api.models import DisabledCommand
import sentry_sdk

from bot import settings
from bot.utils.tools import separator
from bot.utils import context, api


class Bot(commands.Bot):
    def __init__(self, logger: logging.Logger, intents: discord.Intents):
        super().__init__(
            command_prefix=self.setting.prefix,
            description=self.setting.description,
            intents=intents,
            case_insensitive=True
        )

        self.remove_command('help')

        self.logger = logger

        self.start_time = None

        self.app_info = None

        self.loop.create_task(self.track_start())

        self.loop.create_task(self.load_all_extensions())

        self.twitter_api = twitter.Api(**self.setting.twitter)

        self.client_session: aiohttp.ClientSession = aiohttp.ClientSession()

        self.api = api.BotApi(base_url=self.setting.rsatlantis['API_URL'], api_token=self.setting.rsatlantis['API_TOKEN'])

        sentry_sdk.init(
            self.setting.read_data('BOT').get('sentry_dsn'),
            environment=self.setting.mode,
            traces_sample_rate=1.0,
            server_name='AtlantisBot'
        )

    async def post_data(self, url: str, payload: Optional[Dict[str, Any]] = None) -> aiohttp.ClientResponse:
        """
        Posts Data to an URL and returns its response
        """

        request = await self.client_session.post(url, data=payload)

        return request

    async def process_commands(self, message: discord.Message):
        """
        Source: https://github.com/Rapptz/RoboDanny/blob/0c9216245b035fa4655f740c3ce602a5e15bff90/bot.py#L164
        """

        ctx = await self.get_context(message, cls=context.Context)

        if not ctx.command:
            return

        await self.invoke(ctx)

    async def close(self):
        """
        Close aiohttp Client Session and the Bot
        """

        await self.client_session.close()

        await super().close()

    async def send_logs(self, e, tb, ctx: context.Context = None, more_info: object = None):
        dev = self.get_user(self.setting.developer_id)

        if ctx:
            info_embed = discord.Embed(title="__Error Info__", color=discord.Color.dark_red())

            info_embed.add_field(name="Message", value=ctx.message.content, inline=False)

            info_embed.add_field(name="By", value=ctx.author, inline=False)

            info_embed.add_field(name="In Guild", value=ctx.guild, inline=False)

            info_embed.add_field(name="In Channel", value=ctx.channel, inline=False)

            await dev.send(embed=info_embed)

        if more_info:
            extra_embed = discord.Embed(title="__Extra Info__", color=discord.Color.dark_red())

            extra_embed.add_field(name="Info", value=pformat(more_info))

            await dev.send(embed=extra_embed)

        try:
            await dev.send(f"{separator}\n**{e}:**\n```python\n{tb}```")

        except discord.errors.HTTPException:
            logging.error(f"{e}: {tb}")

            try:
                # Split traceback every x characters

                traceback_list = [tb[i:i + 1500] for i in range(0, len(tb), 1500)]

                paginator = commands.Paginator(prefix='```python')

                for tb_list in traceback_list:

                    if len(tb_list) < 1900:

                        paginator.add_line(tb_list)

                for page in paginator.pages:
                    await dev.send(page)

            except Exception as e:
                await dev.send("Erro ao tentar enviar logs.")

                self.logger.error(str(e))

    @property
    def setting(self) -> settings.Settings:
        try:
            with open('bot/bot_settings.json'):
                return settings.Settings()

        except FileNotFoundError:
            with open('bot/bot_settings.json', 'w+') as f:
                json.dump(settings.default_settings, f, indent=4)
                print(
                    f"{colorama.Fore.YELLOW}Settings not found. Default settings file created. "
                    "Edit '/bot/bot_settings.json' to change settings, then reload the bot."
                )

                sys.exit(1)

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

                    print(f'- Loaded Extension: {extension}')

                except Exception as e:

                    error = f'{extension}:\n {type(e).__name__} : {e}'

                    print(f'Failed to load extension {error}')

                    print(traceback.format_exc())

                    errored = True

        print('-' * 10)

        self.disabled_commands()

        return errored

    async def reload_all_extensions(self):

        """Attempts to reload all .py files in /cogs/ as cog extensions"""

        await self.wait_until_ready()

        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing

        errored = False

        for extension in self.get_cogs():

            if extension not in self.setting.disabled_extensions:

                try:
                    self.reload_extension(f'bot.cogs.{extension}')
                    print(f'- Reloaded Extension: {extension}')

                except Exception as e:
                    error = f'{extension}:\n {type(e).__name__} : {e}'
                    print(f'Failed to reload extension {error}')
                    errored = True

        print('-' * 10)

        with open('restart_atl_bot.log', 'w+') as f:
            # If there is an '1' in the file, that means the bot was closed with the
            # !restart command
            text = f.read()
            self.logger.info(f'Bot iniciado com sucesso ({text})')

            if '1' in text:
                await self.app_info.owner.send('Bot reiniciado com sucesso.')

            f.write('0')

        return errored

    def disabled_commands(self):
        for disabled_command in DisabledCommand.objects.all():
            command = self.get_command(disabled_command.name)

            if command:
                command.enabled = False

                print(f"Disabling command {command}.")

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)

        self.app_info = await self.application_info()

        await self.change_presence(activity=discord.Game(name=self.setting.playing_message))

        print(
            f"Bot logged on as '{self.user.name}'\n"
            f"Mode: {self.setting.mode}\n"
            f"Argvs: {sys.argv}\n"
            f"Owner: '{self.app_info.owner}'\n"
            f"ID: '{self.user.id}'\n"
            f"[ Bot Settings ]\n"
            f"- Clan Name: '{self.setting.clan_name}'\n"
            f"- Playing Message: '{self.setting.playing_message}'\n"
            f"- Commands prefix: '{self.setting.prefix}'\n"
            f"- Show titles on claninfo: '{self.setting.show_titles}'"
        )

    async def check_bad_message(self, message: discord.Message) -> bool:
        membro = self.setting.role.get('membro')
        convidado = self.setting.role.get('convidado')
        log_channel: discord.TextChannel = self.get_channel(633465042033180701)

        admin_roles = ['coord_discord', 'org_discord', 'adm_discord']
        roles = [self.setting.admin_roles().get(role) for role in admin_roles]

        unauthorized_mentions = ['@everyone', '@here', f"<@&{membro}>", f"<@&{convidado}>"]

        if any(mention in message.content for mention in unauthorized_mentions):
            if not has_any_role(message.author, *roles):
                embed = discord.Embed(
                    title="__Aviso__",
                    description=separator,
                    color=discord.Color.dark_red(),
                )
                embed.add_field(
                    name=f"Por favor não utilize as menções abaixo sem permissão, insistência resultará em banimento permanente:",
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
                    text="Nosso servidor abriga uma quantidade muito grande de pessoas, tenha bom "
                         "senso e maturidade ao utilizar uma menção que irá notificar centenas de pessoas."
                )

                await log_channel.send(f"{message.author} usou uma menção não permitida no canal #{message.channel}\n\n**__Conteúdo:__** {message.content}")
                await message.delete()
                await message.channel.send(content=message.author.mention, embed=embed)
                return True

        return False

    async def on_message(self, message: discord.Message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        if message.author.bot:
            if self.setting.mode == 'prod':
                if message.content == 'HECK YES!':
                    return await message.channel.send('HECK NO!')
                if message.content == ':(((((':
                    return await message.channel.send('>:))))')
                if self.user.mention in message.content and message.author != self.user:
                    return await message.channel.send('What did you say about me you little *****?!')
            return

        # If in development environment only deal with messages in dev server and channel

        if self.setting.mode == 'dev':
            if not message.guild:
                if message.author.id != self.setting.developer_id:
                    return
            elif message.guild.id != self.setting.dev_guild and message.channel.id != 488106800655106058:
                return

        if self.check_bad_message(message):
            return

        # Replace old Rs Wikia links to the new Rs Wiki links
        if 'http' in message.content and 'runescape.fandom.com/wiki' in message.content:
            urls = re.findall(r"http\S+", message.content)
            formatted_urls = []

            for url in urls:
                if 'runescape.fandom.com/wiki' in url:
                    url = url.replace('runescape.fandom.com/wiki/', 'rs.wiki/w/')
                    formatted_urls.append(url)

            formatted_urls_string = ''
            for url in formatted_urls:
                formatted_urls_string += f'- ***<{url}>***\n'

            plural = 's' if len(formatted_urls) > 1 else ''

            await message.channel.send(
                f'Olá, parece que você usou um ou mais links para a antiga Wiki do RuneScape!'
                f'\n\n'
                f'A wiki antiga não é mais suportada e está muito desatualizada. '
                f'Ao invés do{plural} link{plural} que você enviou, utilize o{plural} link{plural} abaixo:\n\n'
                f'{formatted_urls_string}'
            )
        await self.process_commands(message)

    async def on_member_remove(self, member: discord.Member):
        if self.setting.mode == 'dev':
            return

        log_channel: discord.TextChannel = self.get_channel(633465042033180701)

        embed = discord.Embed(title='Saiu do Servidor', description="\u200B", color=discord.Color.red())

        embed.set_author(name=str(member))

        roles = ', '.join([role.name for role in member.roles]) + '\n'

        embed.add_field(name="Cargos", value=roles.replace('@everyone, ', '').replace('ﾠ', ''))

        embed.set_footer(text=f"• {datetime.datetime.now().strftime('%d/%m/%y - %H:%M')}")

        await log_channel.send(embed=embed)
