from discord.ext import commands

from tests.helpers import FakeContext, make_chat, run_async


def test_atlantisbot_is_hybrid_command():
    chat = make_chat()
    ctx = FakeContext()

    command = chat.atlantisbot
    assert isinstance(command, commands.HybridCommand)
    assert command.name == "atlantisbot"
    assert "atlbot" in command.aliases

    run_async(command.callback(chat, ctx))

    assert ctx.sent_content is None
    assert ctx.sent_embed is not None
    assert ctx.sent_embed.title == "RunePixels"
    assert any(field.name.startswith("!claninfo") for field in ctx.sent_embed.fields)
