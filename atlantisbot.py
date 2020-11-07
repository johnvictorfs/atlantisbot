#!/usr/bin/env python3

import asyncio
import logging
import sys

import colorama
import discord

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bot.orm.settings")
application = get_wsgi_application()  # noqa: F841


async def run(logger: logging.Logger):
    from bot.bot_client import Bot

    intents = discord.Intents.default()
    intents.members = True

    bot = Bot(logger, intents)

    try:
        await bot.start(bot.setting.token)
    except KeyboardInterrupt:
        print(f"{colorama.Fore.RED}KeyBoardInterrupt. Logging out...")
        await bot.logout()
    except discord.errors.LoginFailure:
        print(f"{colorama.Fore.RED}Error: Invalid Token. Please input a valid token in '/bot/bot_settings.json' file.")
        sys.exit(1)


if __name__ == '__main__':
    colorama.init()
    logger = logging.getLogger('discord')
    logger_atl = logging.getLogger('atlantis')

    logger.setLevel(logging.INFO)
    logger_atl.setLevel(logging.INFO)

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8')
    handler_atl = logging.FileHandler(filename='atlantis.log', encoding='utf-8')

    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    handler_atl.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    logger.addHandler(handler)
    logger_atl.addHandler(handler_atl)

    logger_atl.info('Starting bot')
    logger.info('Starting bot')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(logger_atl))
