import datetime
import json
import os


class Settings:
    @staticmethod
    def read_data():
        with open('bot/bot_settings.json', 'r') as f:
            return json.load(f)

    @property
    def clan_settings(self):
        with open('bot/clan_settings.json', 'r') as f:
            return json.load(f)

    @property
    def mode(self):
        return self.read_data()['BOT']['mode']

    @property
    def developer_id(self):
        return self.read_data()['BOT']['developer_id']

    @property
    def guild_id(self):
        return self.read_data()['BOT']['guild_id']

    @property
    def token(self):
        token_ = self.read_data()['BOT']['bot_token']
        if token_ == 'BOT_TOKEN_HERE':
            return os.environ.get('ATLBOT_TOKEN')
        return token_

    @property
    def description(self):
        return self.read_data()['BOT']['description']

    @property
    def dev_guild(self):
        return self.read_data()['BOT']['dev_guild']

    @property
    def playing_message(self):
        return self.read_data()['BOT']['playing_message']

    @property
    def prefix(self):
        return self.read_data()['BOT']['commands_prefix']

    @property
    def disabled_extensions(self):
        return self.read_data()['BOT']['disabled_extensions']

    @property
    def clan_name(self):
        return self.read_data()['RUNESCAPE']['clan_name']

    @property
    def show_titles(self):
        return self.read_data()['RUNESCAPE']['show_titles']

    @property
    def advlog_clans(self):
        return self.read_data()['RUNESCAPE']['advlog_clans']

    @property
    def banner_image(self):
        return self.read_data()['OTHER']['banner_image']

    @property
    def raids_start_date(self):
        return datetime.datetime.strptime(self.read_data()['OTHER']['raids_start_date'], '%H:%M:%S %Y/%m/%d')

    @property
    def not_allowed_in_name(self):
        return self.read_data()['OTHER']['not_allowed_in_name']

    @property
    def server_id(self):
        return self.read_data()['SERVER']['server_id']

    @property
    def chat(self):
        return self.read_data()['SERVER']['chat_id']

    @property
    def role(self):
        return self.read_data()['SERVER']['role_id']


default_settings = {
    "BOT": {
        "mode": "prod",
        "developer_id": 148175892596785152,
        "guild_id": 321012107942428673,
        "bot_token": "BOT_TOKEN_HERE",
        "description": "A discord bot with utilities for RS3 Clans Discords",
        "dev_guild": 268897682066505738,
        "playing_message": "!atlbot",
        "commands_prefix": "!",
        "disabled_extensions": []
    },
    "RUNESCAPE": {
        "clan_name": "Atlantis",
        "show_titles": False,
        "advlog_clans": [
            {
                "name": "Iron Atlantis",
                "chat": 521499765696102420
            },
            {
                "name": "Atlantis",
                "chat": 513848876063784960
            }
        ]
    },
    "OTHER": {
        "banner_image": "http://rsatlantis.com/images/logo.png",
        "raids_start_date": "23:00:00 2019/01/06",
        "not_allowed_in_name": ["discord.me", "discord.gg", "bit.ly", "tinyurl", "tiny.cc", "is.gd", "bc.vc",
                                "twitch.tv", "twitter", "youtube", "youtu.be"]
    },
    "SERVER": {
        "server_id": 321012107942428673,
        "chat_id": {
            "geral": 321012292160454657,
            "anuncios": 467069985270005760,
            "tags_do_server": 382691780996497416,
            "visitantes": 321012324997529602,

            "adv_log": 513848876063784960,
            "links_uteis": 388046792756953090,
            "pvmemes": 333083647991349249,

            "raids": 393104367471034369,
            "raids_chat": 393696030505435136,
            "guia_yaka": 425844417862041610,

            "aod": 499740247647846401,
            "aod_chat": 499740130118991882,
            "guia_aod": 354335920297738240,

            "solak": 474018053693243402,
            "solak_chat": 473194321043259392,

            "vorago_hm": 506660452617420802,
            "vorago_chat": 506660836069212176,

            "drops_e_conquistas": 336182514886377482,
            "discord_bots": 321012588924370945,
            "pof": 417725841271947277,
        },
        "role_id": {
            "admin": 321015469341540352,
            "mod+": 480520619163779085,
            "mod": 321015489583251467,
            "mod_trial": 511283550591647746,
            "membro": 321015529059909674,
            "bot": 324359293304438787,
            "convidado": 321015669883797506,
            "solak_teacher": 484477492510588928,
            "vorago_hm_teacher": 506661260733972489,
            "aod_teacher": 346107676448522240,
            "vorago_teacher": 346107810670706699,
            "raids_teacher": 346107622853836801,
            "pvmemos": 338221796748820502,
            "solak": 473193918293475329,
            "aod_exp": 502236358006276096,
            "aod": 499739627339382825,
            "vorago_hm": 506660926825431043,
            "vorago": 386575400064516097,
            "rots": 497821982264655873,
            "elite_dungeon": 497550738768134183,
            "raids": 376410304277512192,
            "durzag": 488121068834258954,
            "eventos": 409734099800948736,
            "doador": 475407948839911424,
            "filantropo": 475409267751518228,
            "tio_patinhas": 475409581481263104,
            "lannister": 509400346951680001,
            "smaug": 509400283642855427,
            "180k_dpm": 488125956679270410,
            "100k_dpm": 348857911084187648,
            "fortnight": 494634882643787776,
            "osugame": 499261292188794912,
        }
    }
}
