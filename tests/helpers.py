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

    def has_any_role(*_args, **_kwargs):
        return False

    stub_tools.has_any_role = has_any_role
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


@dataclass
class FakeSettings:
    clan_name: str = "Atlantis"
    banner_image: str = "https://example.com/banner.png"
    prefix: str = "!"
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
        self.author = SimpleNamespace(roles=[])

    async def send(self, content=None, *, embed=None):
        self.sent_embed = embed
        self.sent_content = content


def make_chat():
    _stub_modules()
    from bot.cogs.chat import Chat  # noqa: E402

    fake_bot = SimpleNamespace(setting=FakeSettings())
    return Chat(fake_bot)


def run_async(coro: Any):
    import asyncio

    return asyncio.run(coro)
