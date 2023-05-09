import os
import sys
import json
import colorama

import dj_database_url

from bot import settings


try:
    with open("bot/bot_settings.json", "r") as f:
        bot_settings = json.load(f)
        database_url = bot_settings["BOT"]["database_url"]
except FileNotFoundError:
    with open("bot/bot_settings.json", "w+") as f:
        json.dump(settings.default_settings, f, indent=4)
        print(
            f"{colorama.Fore.YELLOW}Settings not found. Default settings file created. "
            "Edit 'bot/bot_settings.json' to change settings, then reload the bot."
        )

        sys.exit(1)

DATABASES = {"default": dj_database_url.parse(database_url)}

INSTALLED_APPS = ("atlantisbot_api",)

SECRET_KEY = os.environ.get("ATLBOT_SECRET_KEY")
