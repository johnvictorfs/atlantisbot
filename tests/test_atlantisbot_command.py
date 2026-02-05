from pathlib import Path
import sys
import types
from types import SimpleNamespace

from discord.ext import commands
import asyncio

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

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

from bot.cogs.chat import Chat  # noqa: E402


class FakeContext:
    def __init__(self):
        self.sent_embed = None
        self.sent_content = None

    async def send(self, *, embed=None, content=None):
        self.sent_embed = embed
        self.sent_content = content


def test_atlantisbot_is_hybrid_command():
    assert isinstance(Chat.atlantisbot, commands.HybridCommand)
    assert Chat.atlantisbot.name == "atlantisbot"
    assert "atlbot" in Chat.atlantisbot.aliases

    fake_bot = SimpleNamespace(
        setting=SimpleNamespace(
            clan_name="Atlantis",
            banner_image="https://example.com/banner.png",
            prefix="!",
        )
    )
    ctx = FakeContext()
    chat = Chat(fake_bot)

    asyncio.run(Chat.atlantisbot.callback(chat, ctx))

    assert ctx.sent_content is None
    assert ctx.sent_embed is not None
    assert ctx.sent_embed.title == "RunePixels"
    assert any(field.name.startswith("!claninfo") for field in ctx.sent_embed.fields)
