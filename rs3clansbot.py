import discord
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
        'bot_token': '',
        'oauth_url': ''
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
        return bot_token, oauth_url
    except KeyError:
        if error_messages is True:
            print("Error: Couldn't read settings.")
            print("Do you wish to re-create them? (y/N)")
            answer = input("\n>> ")
            if answer is 'y' or answer is 'Y':
                generate_settings()
                return 1
            if answer is 'n' or answer is 'N':
                return 1
        else:
            return 1


class BotClient(discord.Client):

    async def on_ready(self):
        print(f"Bot logged on as '{self.user}'")
        print(f"Oauth URL: {OAUTH_URL}")

    # async def on_message(self, message):
    #     print(f"Message from {message.author}: {message.content}")


BOT_TOKEN, OAUTH_URL = ('', '')
if file_exists('bot_settings.ini'):
    BOT_TOKEN, OAUTH_URL = read_settings(file_name='bot_settings')
else:
    generate_settings(file_name='bot_settings')
    print("No settings were found. Generated new settings instead.")
    print("Ending Session. Edit in the necessary settings on 'bot_settings.ini' file and restart the bot.")
    exit(0)

try:
    client = BotClient()
    client.run(BOT_TOKEN)
except discord.errors.LoginFailure:
    print("Invalid Bot Token. Please edit 'bot_token' on 'bot_settings.ini' and restart the bot.")
    exit(0)
