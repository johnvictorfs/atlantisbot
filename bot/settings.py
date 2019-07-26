import datetime
import json
import os


class Settings:
    @staticmethod
    def read_data(section: str):
        with open('bot/bot_settings.json', 'r') as f:
            return json.load(f)[section]

    @property
    def clan_settings(self):
        with open('bot/clan_settings.json', 'r') as f:
            return json.load(f)

    @property
    def mode(self):
        return self.read_data('BOT')['mode']

    @property
    def developer_id(self):
        return self.read_data('BOT')['developer_id']

    @property
    def guild_id(self):
        return self.read_data('BOT')['guild_id']

    @property
    def token(self):
        token_ = self.read_data('BOT')['bot_token']
        if token_ == 'BOT_TOKEN_HERE':
            return os.environ.get('ATLBOT_TOKEN')
        return token_

    @property
    def description(self):
        return self.read_data('BOT')['description']

    @property
    def dev_guild(self):
        return self.read_data('BOT')['dev_guild']

    @property
    def playing_message(self):
        return self.read_data('BOT')['playing_message']

    @property
    def prefix(self):
        return self.read_data('BOT')['commands_prefix']

    @property
    def disabled_extensions(self):
        return self.read_data('BOT')['disabled_extensions']

    @property
    def clan_name(self):
        return self.read_data('RUNESCAPE')['clan_name']

    @property
    def show_titles(self):
        return self.read_data('RUNESCAPE')['show_titles']

    @property
    def advlog_clans(self):
        return self.read_data('RUNESCAPE')['advlog_clans']

    @property
    def banner_image(self):
        return self.read_data('OTHER')['banner_image']

    @property
    def raids_start_date(self):
        return datetime.datetime.strptime(self.read_data('OTHER')['raids_start_date'], '%H:%M:%S %Y/%m/%d')

    @property
    def not_allowed_in_name(self):
        return self.read_data('OTHER')['not_allowed_in_name']

    @property
    def server_id(self):
        return self.read_data('SERVER')['server_id']

    @property
    def welcome_channel_id(self):
        return self.read_data('SERVER')['welcome_channel_id']

    @property
    def welcome_message_id(self):
        return self.read_data('SERVER')['welcome_message_id']

    @property
    def chat(self):
        return self.read_data('SERVER')['chat_id']

    @property
    def role(self):
        return self.read_data('SERVER')['role_id']

    @property
    def roles_channel_id(self):
        return self.read_data('SERVER')['roles_channel_id']

    @property
    def general_roles_id(self):
        return self.read_data('SERVER')['general_roles_id']

    @property
    def pvm_roles_id(self):
        return self.read_data('SERVER')['pvm_roles_id']

    @property
    def react_roles_id(self):
        return self.read_data('SERVER')['react_roles_id']

    @property
    def twitter(self):
        return self.read_data('TWITTER')


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
        "disabled_extensions": [],
        "database_url": "postgres://<user>:<password>@localhost:5432/<database>"
    },
    "TWITTER": {
        "consumer_key": "",
        "consumer_secret": "",
        "access_token_key": "",
        "access_token_secret": ""
    },
    "RUNESCAPE": {
        "clan_name": "Atlantis",
        "show_titles": False,
        "advlog_clans": [
            {
                "name": "Atlantis",
                "chat": 570985364290797590
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
        "welcome_channel_id": 321012107942428673,
        "welcome_message_id": 511313046212182056,
        "roles_channel_id": 382691780996497416,
        "general_roles_id": 488180629775843328,
        "pvm_roles_id": 488180630803316756,
        "react_roles_id": 488180632057544704,
        "chat_id": {
            "vos": 603994903751426083,
            "sos": 576414572206882847,
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

            "aod": 567437912464162816,
            "aod_chat": 499740130118991882,
            "guia_aod": 567444819132022784,

            "solak": 474018053693243402,
            "solak_chat": 473194321043259392,
            "solak_apply": 541779397204508682,

            "vorago_hm": 506660452617420802,
            "vorago_chat": 506660836069212176,

            "drops_e_conquistas": 336182514886377482,
            "discord_bots": 321012588924370945,
            "pof": 417725841271947277,
            "merchant_call": 560980279360094208
        },
        "role_id": {
            "cadarn": 604164034610069537,
            "iorwerth": 604163890380537856,
            "trahaearn": 604163802363068416,
            "ithell": 604163981933805615,
            "crwys": 604162682416922627,
            "hefin": 603992659677151242,
            "amlodd": 603992737641005079,
            "meylir": 603992941509476383,
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
            "200k_dpm": 562063656443969561,
            "180k_dpm": 488125956679270410,
            "100k_dpm": 348857911084187648,
            "fortnight": 494634882643787776,
            "osugame": 499261292188794912,
            "merchant": 560997610954162198,
            "ironmemes": 520670978158624768
        }
    }
}
