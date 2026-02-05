from pathlib import Path
import sys
import types

from discord.ext import commands

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

stub_bot_client = types.ModuleType("bot.bot_client")


class Bot:
    pass


stub_bot_client.Bot = Bot
sys.modules["bot.bot_client"] = stub_bot_client

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


def test_atlantisbot_is_hybrid_command():
    assert isinstance(Chat.atlantisbot, commands.HybridCommand)
    assert Chat.atlantisbot.name == "atlantisbot"
    assert "atlbot" in Chat.atlantisbot.aliases
