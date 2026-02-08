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
    stub_rs3clans = types.ModuleType("rs3clans")

    stub_django_models = types.ModuleType("django.db.models")

    class Q:
        def __init__(self, *_args, **_kwargs):
            pass

    stub_django_models.Q = Q
    sys.modules["django.db.models"] = stub_django_models

    stub_api_models = types.ModuleType("atlantisbot_api.models")

    class DiscordUser:
        objects = SimpleNamespace(filter=lambda **_kwargs: SimpleNamespace(first=lambda: None))

    class DiscordIngameName:
        pass

    stub_api_models.DiscordUser = DiscordUser
    stub_api_models.DiscordIngameName = DiscordIngameName
    sys.modules["atlantisbot_api.models"] = stub_api_models

    stub_rs3clans.Clan = object
    stub_rs3clans.Player = object
    sys.modules["rs3clans"] = stub_rs3clans

    stub_bot_client = types.ModuleType("bot.bot_client")

    class Bot:
        pass

    stub_bot_client.Bot = Bot
    sys.modules["bot.bot_client"] = stub_bot_client

    stub_tools = types.ModuleType("bot.utils.tools")
    stub_tools.right_arrow = "->"
    stub_tools.separator = "---"

    def has_any_role(*_args, **_kwargs):
        return False

    async def get_clan_async(*_args, **_kwargs):
        return []

    def divide_list(value, *_args, **_kwargs):
        return [value]

    stub_tools.has_any_role = has_any_role
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

    stub_raids = types.ModuleType("bot.cogs.raids")

    async def time_till_raids():
        return 0, 0, 0

    stub_raids.time_till_raids = time_till_raids
    sys.modules["bot.cogs.raids"] = stub_raids

    stub_rsworld = types.ModuleType("bot.cogs.rsworld")

    async def grab_world(*_args, **_kwargs):
        return None

    async def get_world(*_args, **_kwargs):
        return None

    def random_world(*_args, **_kwargs):
        return 1

    def filtered_worlds(*_args, **_kwargs):
        return []

    stub_rsworld.grab_world = grab_world
    stub_rsworld.get_world = get_world
    stub_rsworld.random_world = random_world
    stub_rsworld.filtered_worlds = filtered_worlds
    sys.modules["bot.cogs.rsworld"] = stub_rsworld

    stub_roles = types.ModuleType("bot.utils.roles")

    async def check_admin_roles(*_args, **_kwargs):
        return None

    async def check_exp_roles(*_args, **_kwargs):
        return None

    stub_roles.check_admin_roles = check_admin_roles
    stub_roles.check_exp_roles = check_exp_roles
    sys.modules["bot.utils.roles"] = stub_roles



@dataclass
class FakeSettings:
    clan_name: str = "Atlantis"
    banner_image: str = "https://example.com/banner.png"
    prefix: str = "!"
    mode: str = "dev"
    role: dict[str, int] | None = None
    chat: dict[str, int] | None = None

    def __post_init__(self):
        if self.role is None:
            self.role = {"pvm_teacher": 123, "aod": 456, "aod_learner": 789}
        if self.chat is None:
            self.chat = {"aod": 321}


class FakeContext:
    def __init__(self):
        self.sent_embed = None
        self.sent_content = None
        self.sent_messages = []
        self.author = SimpleNamespace(roles=[])
        self.interaction = None

    async def send(self, content=None, *, embed=None):
        self.sent_embed = embed
        self.sent_content = content
        self.sent_messages.append({"content": content, "embed": embed})


def make_chat():
    _stub_modules()
    from bot.cogs.chat import Chat  # noqa: E402

    fake_bot = SimpleNamespace(setting=FakeSettings())
    return Chat(fake_bot)


def run_async(coro: Any):
    import asyncio

    return asyncio.run(coro)


def make_clan():
    _stub_modules()
    from bot.cogs.clan import Clan  # noqa: E402

    clan_settings = {
        "Recruit": {"Emoji": "R", "Translation": "Recruta"},
        "Corporal": {"Emoji": "C", "Translation": "Cabo"},
        "Sergeant": {"Emoji": "S", "Translation": "Sargento"},
        "Lieutenant": {"Emoji": "L", "Translation": "Tenente"},
        "Captain": {"Emoji": "CP", "Translation": "Capitão"},
        "General": {"Emoji": "G", "Translation": "General"},
    }
    fake_bot = SimpleNamespace(setting=SimpleNamespace(clan_settings=clan_settings))
    return Clan(fake_bot)


def make_authentication():
    _stub_modules()
    from bot.cogs.authentication import UserAuthentication  # noqa: E402

    fake_bot = SimpleNamespace(setting=FakeSettings())
    return UserAuthentication(fake_bot)
