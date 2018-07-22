import discord
from bot.definesettings import file_exists, read_settings, generate_settings


def start_settings():
    if file_exists('bot_settings.ini'):
        try:
            bot_token, oauth_url, playing_now, clan_name = read_settings(file_name='bot_settings')
        except TypeError:
            print("Error when reading settings.")
            return 1
    else:
        generate_settings(file_name='bot_settings')
        print("No settings were found. Generated new settings instead.")
        print("Ending Session. Edit in the necessary settings on 'bot_settings.ini' file and restart the bot.")
        return 0
    return bot_token, oauth_url, playing_now, clan_name


class BotClient(discord.Client):

    async def on_ready(self):
        await self.change_presence(game=discord.Game(name=PLAYING_NOW))
        print(f"Bot logged on as '{self.user}'")
        print(f"Oauth URL: {OAUTH_URL}")
        print()
        print("[ Bot Settings ]")
        print(f"- Clan Name: '{CLAN_NAME}'")
        print(f"- Playing Message: '{PLAYING_NOW}'")

    # async def on_message(self, message):
    #     print(f"Message from {message.author}: {message.content}")


if __name__ == '__main__':
    BOT_TOKEN, OAUTH_URL, PLAYING_NOW, CLAN_NAME = start_settings()
    try:
        client = BotClient()
        client.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("Invalid Bot Token. Please edit 'bot_token' on 'bot_settings.ini' and restart the bot.")
        exit(0)
