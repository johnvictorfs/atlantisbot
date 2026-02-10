from types import SimpleNamespace

from discord.ext import commands

from tests.helpers import FakeContext, make_clan, run_async


def test_ranks_is_hybrid_command():
    clan = make_clan()

    command = clan.ranks
    assert isinstance(command, commands.HybridCommand)
    assert command.name == "ranks"
    assert "rank" in command.aliases


def test_ranks_prefix_suggests_slash(monkeypatch):
    clan_cog = make_clan()
    ctx = FakeContext()

    member = SimpleNamespace(exp=1, rank="Recruit", name="Test")

    monkeypatch.setattr("bot.cogs.clan.rs3clans.Clan", lambda *_args, **_kwargs: [member])

    run_async(clan_cog.ranks.callback(clan_cog, ctx, clan="Atlantis"))

    assert len(ctx.sent_messages) == 2
    assert "use o comando de barra `/ranks`" in ctx.sent_messages[0]["content"]
    assert ctx.sent_messages[1]["embed"] is not None


def test_ranks_has_clan_choices():
    clan_cog = make_clan()

    command = clan_cog.ranks

    app_command = command.app_command
    clan_parameter = next(parameter for parameter in app_command.parameters if parameter.name == "clan")

    assert [choice.name for choice in clan_parameter.choices] == ["Atlantis", "Atlantis Argus"]
    assert [choice.value for choice in clan_parameter.choices] == ["atlantis", "argus"]


def test_ranks_default_clan_is_atlantis():
    clan_cog = make_clan()

    command = clan_cog.ranks
    clan_parameter = next(parameter for parameter in command.app_command.parameters if parameter.name == "clan")

    assert clan_parameter.default == "atlantis"
