# Standard lib imports
import configparser
import json
import io
import os


def file_exists(file):
    try:
        with open(file, 'r'):
            return True
    except FileNotFoundError:
        return False


def generate_settings(file_name='bot_settings'):
    config = configparser.ConfigParser()

    config['DISCORD'] = {
        'bot_token': 'BOT_TOKEN_HERE',
        'oauth_url': 'OAUTH_URL_HERE',
        'playing_now': 'PLAYING_MESSAGE',
        'commands_prefix': '!',
        'bot_description': 'A discord bot with utilities for RS3 Clans Discords',
        'language': 'English',
        'mod_id': '<@&321015489583251467>',
        'admin_id': '<@&321015469341540352>',
        'raids_teacher_id': '<@&346107622853836801>',
        'raids_chat_id': '<#393696030505435136>',
        'raids_notif_chat_id': '393104367471034369'
    }

    config['RUNESCAPE'] = {
        'clan_name': 'CLAN_NAME_HERE',
        'icon_url': 'https://secure.runescape.com/m=avatar-rs/{}/chat.png',
        'runeclan_url': 'https://runeclan.com/user/{}',
        'clan_banner_url': 'http://services.runescape.com/m=avatar-rs/l=3/a=869/{}/clanmotif.png',
        'show_titles': 'false',
    }

    config['COGS'] = {
        'disabled': 'chat,clan,embeds,error_handler,raids_day,welcome_message'
    }

    with open(f"{file_name}.ini", 'w') as config_file_:
        config.write(config_file_)
        return


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
    MOD_ID = config_file['DISCORD']['mod_id']
    ADMIN_ID = config_file['DISCORD']['admin_id']
    RAIDS_TEACHER_ID = config_file['DISCORD']['raids_teacher_id']
    RAIDS_CHAT_ID = config_file['DISCORD']['raids_chat_id']
    RAIDS_NOTIF_CHAT_ID = config_file['DISCORD']['raids_notif_chat_id']

    DISABLED_COGS = config_file['COGS']['disabled'].split(',')

    CLAN_NAME = config_file['RUNESCAPE']['clan_name']
    SHOW_TITLES = config_file['RUNESCAPE']['show_titles']

    if SHOW_TITLES.lower() == 'false':
        SHOW_TITLES = False
    else:
        SHOW_TITLES = True
elif os.environ.get('ATLBOT_HEROKU') == 'prod':
    config = configparser.ConfigParser()

    config['DISCORD'] = {
        'bot_token': os.environ['ATLBOT_TOKEN'],
        'oauth_url': 'N/A',
        'playing_now': '!atlcommands',
        'commands_prefix': '!',
        'bot_description': 'A discord bot with utilities for RS3 Clans Discords',
        'language': 'Portuguese',
        'mod_id': '<@&321015489583251467>',
        'admin_id': '<@&321015469341540352>',
        'raids_teacher_id': '<@&346107622853836801>',
        'raids_chat_id': '<#393696030505435136>',
        'raids_notif_chat_id': '393104367471034369'
    }

    config['RUNESCAPE'] = {
        'clan_name': 'Atlantis',
        'icon_url': 'https://secure.runescape.com/m=avatar-rs/{}/chat.png',
        'runeclan_url': 'https://runeclan.com/user/{}',
        'clan_banner_url': 'http://services.runescape.com/m=avatar-rs/l=3/a=869/{}/clanmotif.png',
        'show_titles': 'false',
    }

    config['COGS'] = {
        'disabled': 'embeds'
    }

else:
    answer = input("Settings not found. Do you wish the re-create them? (y/N)\n\n>> ")
    if answer is 'y' or answer is 'Y':
        generate_settings()
        print("Generated new settings. Edit them in 'bot_settings.ini' and then restart the Bot.")
        exit(0)
    else:
        raise KeyError("Couldn't read settings. Verify if 'bot_settings.ini' exists and is correctly configured.")

clan_settings_ = {
    "Owner":
    {
        "Rank": "Owner",
        "Emoji": "<:owner:458788729641762826>",
        "Translation": "Líder"
    },

    "Deputy Owner":
    {
        "Rank": "Deputy Owner",
        "Emoji": "<:deputy_owner:458788729507676160>",
        "Translation": "Vice-Líder"
    },

    "Overseer":
    {
        "Rank": "Overseer",
        "Emoji": "<:overseer:458788729893683201>",
        "Translation": "Fiscal"
    },

    "Coordinator":
    {
        "Rank": "Coordinator",
        "Emoji": "<:coordinator:458788729562202112>",
        "Translation": "Coordenador"
    },

    "Organiser":
    {
        "Rank": "Organiser",
        "Emoji": "<:organiser:458788729503612948>",
        "Translation": "Organizador"
    },

    "Admin":
    {
        "Rank": "Admin",
        "Emoji": "<:admin:458788729494962197>",
        "Translation": "Admin"
    },

    "General":
    {
        "Rank": "General",
        "Emoji": "<:general:458788729318932501>",
        "Translation": "General"
    },

    "Captain":
    {
        "Rank": "Captain",
        "Emoji": "<:captain:458788729738362885>",
        "Translation": "Capitão"
    },

    "Lieutenant":
    {
        "Rank": "Lieutenant",
        "Emoji": "<:lieutenant:458788729687900190>",
        "Translation": "Tenente"
    },

    "Sergeant":
    {
        "Rank": "Sergeant",
        "Emoji": "<:sergeant:458788729432309761>",
        "Translation": "Sargento"
    },

    "Corporal":
    {
        "Rank": "Corporal",
        "Emoji": "<:corporal:458788729612402688>",
        "Translation": "Cabo"
    },

    "Recruit":
    {
        "Rank": "Recruit",
        "Emoji": "<:recruit:458788730044416001>",
        "Translation": "Recruta"
    }
}
CLAN_SETTINGS = json.load(clan_settings_)

with open('messages.json', encoding='utf-8') as f:
    MESSAGES = json.load(f)
