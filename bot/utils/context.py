from atlantisbot_api.models import DiscordUser
from bot.settings import Settings
import io
import discord
import asyncio
from typing import Optional

from discord.ext import commands


class Context(commands.Context):
    """
    Source: https://github.com/Rapptz/RoboDanny/blob/ac3a0ed64381050c37761d358d4af90b89ec1ca3/cogs/utils/context.py
    """

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self.bot = self.bot
        self.setting: Settings = self.bot.setting

    async def entry_to_code(self, entries):
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"{name:<{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    async def indented_entry_to_code(self, entries):
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"\u200b{name:>{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    def __repr__(self):
        # we need this for our cache key strategy
        return "<Context>"

    def get_user(self) -> Optional[DiscordUser]:
        user = DiscordUser.objects.filter(discord_id=str(self.author.id)).first()

        if user:
            return user
        return None

    async def disambiguate(self, matches, entry):
        if len(matches) == 0:
            raise ValueError("Nenhum resultado encontrado.")

        if len(matches) == 1:
            return matches[0]

        await self.send(
            "There are too many matches... Which one did you mean? **Only say the number**."
        )
        await self.send(
            "\n".join(
                f"{index}: {entry(item)}" for index, item in enumerate(matches, 1)
            )
        )

        def check(m: discord.Message):
            return (
                m.content.isdigit()
                and m.author.id == self.author.id
                and m.channel.id == self.channel.id
            )

        await self.release()

        # only give them 3 tries.
        try:
            for i in range(3):
                try:
                    message = await self.bot.wait_for(
                        "message", check=check, timeout=30.0
                    )
                except asyncio.TimeoutError:
                    raise ValueError("Took too long. Goodbye.")

                index = int(message.content)
                try:
                    return matches[index - 1]
                except Exception:
                    await self.send(
                        f"Please give me a valid number. {2 - i} tries remaining..."
                    )

            raise ValueError("Too many tries. Goodbye.")
        finally:
            await self.acquire()

    async def prompt(
        self, message: str, *, timeout=60.0, delete_after=True, author_id=None
    ) -> Optional[bool]:
        """An interactive reaction confirmation dialog.
        Parameters
        -----------
        message: str
            The message to show along with the prompt.
        timeout: float
            How long to wait before returning.
        delete_after: bool
            Whether to delete the confirmation message after we're done.
        author_id: Optional[int]
            The member who should respond to the prompt. Defaults to the author of the
            Context's message.
        Returns
        --------
        Optional[bool]
            ``True`` if explicit confirm,
            ``False`` if explicit deny,
            ``None`` if deny due to timeout
        """

        if not self.channel.permissions_for(self.me).add_reactions:
            raise RuntimeError("Bot does not have Add Reactions permission.")

        fmt = message

        author_id = author_id or self.author.id
        msg = await self.send(fmt)

        confirm = None

        def check(payload):
            nonlocal confirm

            if payload.message_id != msg.id or payload.user_id != author_id:
                return False

            codepoint = str(payload.emoji)

            if codepoint == "\N{WHITE HEAVY CHECK MARK}":
                confirm = True
                return True
            elif codepoint == "\N{CROSS MARK}":
                confirm = False
                return True

            return False

        for emoji in ("\N{WHITE HEAVY CHECK MARK}", "\N{CROSS MARK}"):
            await msg.add_reaction(emoji)

        try:
            await self.bot.wait_for("raw_reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None

        try:
            if delete_after:
                await msg.delete()
        finally:
            return confirm

    @staticmethod
    def tick(opt: Optional[bool] = None, label: str = None):
        lookup = {True: ":white_check_mark:", False: ":x:", None: ":heavy_check_mark:"}

        emoji = lookup.get(opt, "<:greyTick:563231201280917524>")

        if label:
            return f"{emoji} {label}"
        return emoji

    async def show_help(self, command=None):
        """Shows the help command for the specified command if given.
        If no command is given, then it'll show help for the current
        command.
        """
        cmd = self.bot.get_command("help")
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)

    async def safe_send(self, content: str, *, escape_mentions=True, **kwargs):
        """Same as send except with some safe guards.
        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop("file", None)
            return await self.send(
                file=discord.File(fp, filename="message_too_long.txt"), **kwargs
            )
        else:
            return await self.send(content)
