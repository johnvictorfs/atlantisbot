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
        'commands_prefix': '!'
    }

    config['RUNESCAPE'] = {
        'clan_name': 'CLAN_NAME_HERE'
    }

    with open(f"{file_name}.ini", 'w') as config_file:
        config.write(config_file)
        return
