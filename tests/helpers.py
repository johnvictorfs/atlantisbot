from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


def _stub_modules():
    if getattr(sys.modules.get("rs3clans"), "_is_stub", False):
        return
    stub_rs3clans = types.ModuleType("rs3clans")
    stub_rs3clans._is_stub = True

    class ClanMember:
        def __init__(self, name: str, exp: int, rank: str):
            self.name = name
            self.exp = exp
            self.rank = rank

    class Clan:
        def __init__(self, *args, **kwargs):
            self.members = list(getattr(stub_rs3clans, "_members", []))

        def __iter__(self):
            return iter(self.members)

    class Player:
        def __init__(self, *args, **kwargs):
            self.exists = True
            self.name = "Player"
            self.clan = "Atlantis"
            self.private_profile = False

    class ClanNotFoundError(Exception):
        pass

    stub_rs3clans.Clan = Clan
    stub_rs3clans.ClanMember = ClanMember
    stub_rs3clans.Player = Player
    stub_rs3clans.ClanNotFoundError = ClanNotFoundError
    sys.modules["rs3clans"] = stub_rs3clans

    stub_django = types.ModuleType("django")
    stub_django_db = types.ModuleType("django.db")
    stub_django_models = types.ModuleType("django.db.models")

    class Q:
        def __init__(self, *args, **kwargs):
            pass

    stub_django_models.Q = Q
    stub_django_db.models = stub_django_models
    stub_django.db = stub_django_db
    sys.modules["django"] = stub_django
    sys.modules["django.db"] = stub_django_db
    sys.modules["django.db.models"] = stub_django_models

    stub_api = types.ModuleType("atlantisbot_api")
    stub_api_models = types.ModuleType("atlantisbot_api.models")

    class DiscordUser:
        objects = []

    class DiscordIngameName:
        objects = []

    stub_api_models.DiscordUser = DiscordUser
    stub_api_models.DiscordIngameName = DiscordIngameName
    stub_api.models = stub_api_models
    sys.modules["atlantisbot_api"] = stub_api
    sys.modules["atlantisbot_api.models"] = stub_api_models

    stub_bot_client = types.ModuleType("bot.bot_client")

    class Bot:
        pass

    stub_bot_client.Bot = Bot
    sys.modules["bot.bot_client"] = stub_bot_client

    stub_tools = types.ModuleType("bot.utils.tools")
    stub_tools.right_arrow = "->"
    stub_tools.separator = "----"

    def has_any_role(*_args, **_kwargs):
        return False

    stub_tools.has_any_role = has_any_role

    async def get_clan_async(*_args, **_kwargs):
        return stub_rs3clans.Clan()

    def divide_list(items, size):
        return [items[i : i + size] for i in range(0, len(items), size)]

    stub_tools.get_clan_async = get_clan_async
    stub_tools.divide_list = divide_list
    sys.modules["bot.utils.tools"] = stub_tools

    stub_checks = types.ModuleType("bot.utils.checks")

    async def is_authenticated(ctx):
        return True

    async def is_admin(ctx):
        return True

    stub_checks.is_authenticated = is_authenticated
    stub_checks.is_admin = is_admin
    sys.modules["bot.utils.checks"] = stub_checks

    stub_context = types.ModuleType("bot.utils.context")

    class Context:
        pass

    stub_context.Context = Context
    sys.modules["bot.utils.context"] = stub_context

    stub_rsworld = types.ModuleType("bot.cogs.rsworld")

    async def grab_world(*_args, **_kwargs):
        return None

    async def get_world(*_args, **_kwargs):
        return None

    def random_world(*_args, **_kwargs):
        return None

    def filtered_worlds(*_args, **_kwargs):
        return []

    stub_rsworld.grab_world = grab_world
    stub_rsworld.get_world = get_world
    stub_rsworld.random_world = random_world
    stub_rsworld.filtered_worlds = filtered_worlds
    sys.modules["bot.cogs.rsworld"] = stub_rsworld

    stub_roles = types.ModuleType("bot.utils.roles")

    def check_admin_roles(*_args, **_kwargs):
        return None

    def check_exp_roles(*_args, **_kwargs):
        return None

    stub_roles.check_admin_roles = check_admin_roles
    stub_roles.check_exp_roles = check_exp_roles
    sys.modules["bot.utils.roles"] = stub_roles

    stub_raids = types.ModuleType("bot.cogs.raids")

    async def time_till_raids():
        return 0, 0, 0

    stub_raids.time_till_raids = time_till_raids
    sys.modules["bot.cogs.raids"] = stub_raids


@dataclass
class FakeSettings:
    clan_name: str = "Atlantis"
    banner_image: str = "https://example.com/banner.png"
    prefix: str = "!"
    role: dict[str, int] | None = None
    chat: dict[str, int] | None = None
    clan_settings: dict[str, dict[str, str]] | None = None
    server_id: int = 123

    def __post_init__(self):
        if self.role is None:
            self.role = {"pvm_teacher": 123, "aod": 456, "aod_learner": 789}
        if self.chat is None:
            self.chat = {"aod": 321}
        if self.clan_settings is None:
            self.clan_settings = {
                "Recruit": {"Emoji": "R"},
                "Corporal": {"Emoji": "C"},
                "Sergeant": {"Emoji": "S"},
                "Lieutenant": {"Emoji": "L"},
                "Captain": {"Emoji": "CPT"},
                "General": {"Emoji": "G"},
            }


class FakeContext:
    def __init__(self):
        self.sent_embed = None
        self.sent_content = None
        self.author = SimpleNamespace(roles=[], id=1)
        self.messages = []
        self.interaction = None

    async def send(self, content=None, *, embed=None):
        self.sent_embed = embed
        self.sent_content = content
        self.messages.append({"content": content, "embed": embed})


def make_chat():
    _stub_modules()
    from bot.cogs.chat import Chat  # noqa: E402

    fake_bot = SimpleNamespace(setting=FakeSettings())
    return Chat(fake_bot)


def make_clan():
    _stub_modules()
    from bot.cogs.clan import Clan  # noqa: E402

    fake_bot = SimpleNamespace(setting=FakeSettings())
    return Clan(fake_bot)


def make_authentication():
    _stub_modules()
    from bot.cogs.authentication import UserAuthentication  # noqa: E402

    class FakeGuild:
        def get_member(self, _member_id):
            return None

    class FakeBot:
        def __init__(self):
            self.setting = FakeSettings()

        def get_guild(self, _guild_id):
            return FakeGuild()

    return UserAuthentication(FakeBot())


def set_stub_clan_members(members):
    _stub_modules()
    sys.modules["rs3clans"]._members = members


def get_stub_rs3clans():
    _stub_modules()
    return sys.modules["rs3clans"]


def run_async(coro: Any):
    import asyncio

    return asyncio.run(coro)
