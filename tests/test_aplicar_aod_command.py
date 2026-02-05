from tests.helpers import FakeContext, make_chat, run_async


def test_aplicar_aod_sends_text_message():
    chat = make_chat()
    ctx = FakeContext()

    run_async(chat.aplicar_aod.callback(chat, ctx))

    assert ctx.sent_embed is None
    assert ctx.sent_content is not None
    assert "Você aplicou para receber a tag de AoD" in ctx.sent_content
