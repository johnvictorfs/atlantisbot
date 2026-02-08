from discord.ext import commands

from tests.helpers import make_authentication


def test_aplicar_role_is_hybrid_command():
    authentication = make_authentication()
    command = authentication.aplicar_role

    assert isinstance(command, commands.HybridCommand)
    assert command.name == "aplicar"
    assert "membro" in command.aliases
