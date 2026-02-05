from discord.ext import commands

from tests.helpers import (
    FakeContext,
    get_stub_rs3clans,
    make_clan,
    run_async,
    set_stub_clan_members,
)


def test_ranks_is_hybrid_command_and_suggests_slash_usage():
    rs3clans = get_stub_rs3clans()
    set_stub_clan_members(
        [
            rs3clans.ClanMember(name="Member", exp=300_000_000, rank="Corporal"),
        ]
    )

    clan = make_clan()
    ctx = FakeContext()

    command = clan.ranks
    assert isinstance(command, commands.HybridCommand)
    assert command.name == "ranks"

    run_async(command.callback(clan, ctx, clan="Atlantis"))

    assert ctx.messages[0]["content"] == "Dica: você também pode usar o comando `/ranks`."
    assert ctx.sent_embed is not None
    assert any("Member" == field.name for field in ctx.sent_embed.fields)
