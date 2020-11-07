import os
import sys
import json

import dj_database_url


try:
    with open('bot/bot_settings.json', 'r') as f:
        settings = json.load(f)
        database_url = settings['BOT']['database_url']
except FileNotFoundError:
    print('No bot/bot_settings.json file found.')
    sys.exit(1)

DATABASES = {
    'default': dj_database_url.parse(database_url)
}

INSTALLED_APPS = (
    'atlantisbot_api',
)

SECRET_KEY = os.environ.get('ATLBOT_SECRET_KEY')
