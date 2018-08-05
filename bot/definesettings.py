import configparser


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
        'language': 'english'
    }

    config['RUNESCAPE'] = {
        'clan_name': 'CLAN_NAME_HERE'
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
