from discord.ext import commands

from tests.helpers import FakeContext, make_authentication, run_async


def test_aplicar_is_hybrid_command_and_sends_invite_message():
    authentication = make_authentication()
    ctx = FakeContext()

    command = authentication.aplicar_role
    assert isinstance(command, commands.HybridCommand)
    assert command.name == "aplicar"

    run_async(command.callback(authentication, ctx))

    assert any(
        message["content"]
        and "Você precisa estar no Discord do Atlantis" in message["content"]
        for message in ctx.messages
    )
