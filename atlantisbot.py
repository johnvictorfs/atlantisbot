#!/usr/bin/env python3

import asyncio
import logging
import sys

import colorama
import discord

from bot.bot_client import Bot


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


if __name__ == '__main__':
    colorama.init()
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
