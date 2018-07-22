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
        'playing_now': ''
    }

    config['RUNESCAPE'] = {
        'clan_name': 'CLAN_NAME_HERE'
    }

    with open(f"{file_name}.ini", 'w') as config_file:
        config.write(config_file)
        return


def read_settings(file_name='bot_settings', progress_messages=True, error_messages=True):
    config = configparser.ConfigParser()
    config.read(f"{file_name}.ini")

    try:
        if progress_messages is True:
            print("Reading settings...")

        bot_token = config['DISCORD']['bot_token']
        oauth_url = config['DISCORD']['oauth_url']
        playing_now = config['DISCORD']['playing_now']

        clan_name = config['RUNESCAPE']['clan_name']

        return bot_token, oauth_url, playing_now, clan_name
    except KeyError:
        if error_messages is True:
            print("Error: Couldn't read settings properly.")
            print("Do you wish to re-create them? (y/N)")
            answer = input("\n>> ")
            if answer is 'y' or answer is 'Y':
                print("Generating new settings.")
                generate_settings()
            if answer is 'n' or answer is 'N':
                print("Not generating new settings.")
        print("Restart the bot so changes can take effect.")
        return 1



