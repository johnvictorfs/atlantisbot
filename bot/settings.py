from typing import Dict, Optional, List
import datetime
import json
import os


class Settings:
    @staticmethod
    def read_data(section: str) -> dict:
        with open("bot/bot_settings.json", "r") as f:
            return json.load(f)[section]

    @property
    def clan_settings(self):
        with open("bot/data/clan_settings.json", "r") as f:
            return json.load(f)

    @property
    def mode(self) -> str:
        return self.read_data("BOT")["mode"]

    @property
    def developer_id(self) -> int:
        return self.read_data("BOT")["developer_id"]

    @property
    def guild_id(self) -> int:
        return self.read_data("BOT")["guild_id"]

    @property
    def token(self) -> Optional[str]:
        token_ = self.read_data("BOT")["bot_token"]
        if token_ == "BOT_TOKEN_HERE":
            return os.environ.get("ATLBOT_TOKEN")
        return token_

    @property
    def description(self):
        return self.read_data("BOT")["description"]

    @property
    def dev_guild(self):
        return self.read_data("BOT")["dev_guild"]

    @property
    def playing_message(self):
        return self.read_data("BOT")["playing_message"]

    @property
    def prefix(self):
        return self.read_data("BOT")["commands_prefix"]

    @property
    def disabled_extensions(self):
        return self.read_data("BOT")["disabled_extensions"]

    @property
    def clan_name(self):
        return self.read_data("RUNESCAPE")["clan_name"]

    @property
    def clan_names(self) -> List[str]:
        return self.read_data("RUNESCAPE")["clan_names"]

    @property
    def clans(self) -> Dict[str, int]:
        return self.read_data("RUNESCAPE")["clans"]

    @property
    def show_titles(self):
        return self.read_data("RUNESCAPE")["show_titles"]

    @property
    def advlog_clans(self):
        return self.read_data("RUNESCAPE")["advlog_clans"]

    @property
    def banner_image(self):
        return self.read_data("OTHER")["banner_image"]

    @property
    def whatsapp_url(self) -> str:
        return self.read_data("OTHER")["whatsapp_url"]

    @property
    def donation_url(self) -> str:
        return self.read_data("OTHER")["donation_url"]

    @property
    def raids_start_date(self) -> datetime.datetime:
        return datetime.datetime.strptime(
            self.read_data("OTHER")["raids_start_date"], "%H:%M:%S %Y/%m/%d"
        )

    @property
    def not_allowed_in_name(self):
        return self.read_data("OTHER")["not_allowed_in_name"]

    @property
    def server_id(self):
        return self.read_data("SERVER")["server_id"]

    @property
    def welcome_channel_id(self):
        return self.read_data("SERVER")["welcome_channel_id"]

    @property
    def welcome_message_id(self):
        return self.read_data("SERVER")["welcome_message_id"]

    @property
    def chat(self) -> Dict[str, int]:
        return self.read_data("SERVER")["chat_id"]

    @property
    def role(self) -> Dict[str, int]:
        return self.read_data("SERVER")["role_id"]

    @property
    def roles_channel_id(self):
        return self.read_data("SERVER")["roles_channel_id"]

    @property
    def general_roles_id(self):
        return self.read_data("SERVER")["general_roles_id"]

    @property
    def pvm_roles_id(self):
        return self.read_data("SERVER")["pvm_roles_id"]

    @property
    def react_roles_id(self):
        return self.read_data("SERVER")["react_roles_id"]

    @property
    def merchant_message(self):
        return self.read_data("SERVER")["merchant_message_id"]

    @property
    def twitter(self):
        return self.read_data("TWITTER")

    @property
    def authorization(self):
        return self.read_data("AUTHORIZATION")

    @property
    def rsatlantis(self):
        return self.read_data("RSATLANTIS")

    def admin_roles(self):
        return self.read_data("RS_ADMIN")


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
        "database_url": "postgresql://postgres:postgres@localhost:5455/postgres",
    },
    "TWITTER": {
        "consumer_key": "",
        "consumer_secret": "",
        "access_token_key": "",
        "access_token_secret": "",
    },
    "RS_ADMIN": {
        "coord_discord": 701555954935922778,
        "org_discord": 701555670054338581,
        "adm_discord": 701556060166553641,
        "rs_owner": 680012958503665669,
        "rs_deputy_owner": 680012880565108751,
        "rs_overseer": 680012822452633647,
        "rs_coord": 680012585197764643,
        "rs_org": 680012163305177110,
        "rs_admin": 680012769294155784,
    },
    "RUNESCAPE": {
        "clan_name": "Atlantis",
        "clan_names": ["Atlantis", "Atlantis Argus"],
        "clans": {"Atlantis": 184644, "Atlantis Argus": 395277},
        "show_titles": False,
        "advlog_clans": [{"name": "Atlantis", "chat": 570985364290797590}],
    },
    "AUTHORIZATION": {"name": "", "type": "", "data": ""},
    "RSATLANTIS": {"API_URL": "", "API_TOKEN": ""},
    "OTHER": {
        "donation_url": "",
        "banner_image": "http://rsatlantis.com/images/logo.png",
        "raids_start_date": "23:00:00 2019/01/06",
        "not_allowed_in_name": [
            "discord.me",
            "discord.gg",
            "bit.ly",
            "tinyurl",
            "tiny.cc",
            "is.gd",
            "bc.vc",
            "twitch.tv",
            "twitter",
            "youtube",
            "youtu.be",
        ],
    },
    "SERVER": {
        "server_id": 321012107942428673,
        "welcome_channel_id": 321012107942428673,
        "welcome_message_id": 511313046212182056,
        "roles_channel_id": 382691780996497416,
        "general_roles_id": 488180629775843328,
        "pvm_roles_id": 488180630803316756,
        "react_roles_id": 488180632057544704,
        "merchant_message_id": 644013123354755113,
        "chat_id": {
            "auth_feedback": 638134883050586125,
            "auth": 589229053790388289,
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
            "merchant_call": 560980279360094208,
        },
        "role_id": {
            "argus": 780415560013578240,
            "administrador": 680012769294155784,
            "organizador": 680012163305177110,
            "coordenador": 680012585197764643,
            "fiscal": 680012822452633647,
            "vice_lider": 680012880565108751,
            "lider": 680012958503665669,
            "aprendiz_pvm": 732001297045389402,
            "cadarn": 604164034610069537,
            "iorwerth": 604163890380537856,
            "trahaearn": 604163802363068416,
            "ithell": 604163981933805615,
            "crwys": 604162682416922627,
            "hefin": 603992659677151242,
            "amlodd": 603992737641005079,
            "meilyr": 603992941509476383,
            "membro": 321015529059909674,
            "bot": 324359293304438787,
            "convidado": 321015669883797506,
            "pvm_teacher": 484477492510588928,
            "pvmemos": 338221796748820502,
            "solak": 473193918293475329,
            "aod_exp": 502236358006276096,
            "aod": 499739627339382825,
            "aod_learner": 567439632518742019,
            "solak_learner": 527640042412441601,
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
            "ironmemes": 520670978158624768,
            "among_us": 772253379119677532,
        },
    },
}
