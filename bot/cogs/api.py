from discord.ext import commands
import aiohttp
import discord
import traceback

from bot.bot_client import Bot


class AtlantisBotApi(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        self.socket_client_task = self.bot.loop.create_task(self.socket_client())

    def cog_unload(self):
        self.socket_client_task.cancel()

    async def socket_client(self):
        """
        Connect to Atlantisbot's Websockets API
        """
        await self.bot.wait_until_ready()

        try:
            async with self.bot.client_session.ws_connect('http://localhost:8000/ws', autoclose=True) as ws:
                ws: aiohttp.client_ws.ClientWebSocketResponse

                async for msg in ws:
                    try:
                        msg: aiohttp.WSMessage

                        if msg.type == aiohttp.WSMsgType.TEXT and msg.data:
                            ws: aiohttp.Client

                            data = msg.json()

                            guild: discord.Guild = self.bot.get_guild(int(data['guild_id']))

                            if guild:
                                channel: discord.TextChannel = guild.get_channel(int(data['channel_id']))

                                if channel:
                                    if data.get('embed'):
                                        # Send embed if passed
                                        color = None
                                        if data['embed'].get('color'):
                                            # Convert str hex color to int, remove starting '#' if it exists
                                            color = int(data['embed']['color'].replace('#', ''), 16)

                                        embed = discord.Embed(
                                            title=data['embed']['title'],
                                            description=data['embed']['description'],
                                            color=color,
                                            thumbnail=data['embed'].get('thumbnail')
                                        )

                                        if data['embed'].get('thumbnail'):
                                            embed.set_thumbnail(url=data['embed']['thumbnail'])

                                        if data['embed'].get('footer'):
                                            embed.set_footer(text=data['embed']['footer'])

                                        if data['embed'].get('embed_fields'):
                                            for field in data['embed']['embed_fields']:
                                                embed.add_field(
                                                    name=field['name'],
                                                    value=field['value'], inline=field['inline']
                                                )

                                        message: discord.Message = await channel.send(
                                            content=data.get('content'),
                                            embed=embed
                                        )
                                    else:
                                        message: discord.Message = await channel.send(data.get('content'))

                                    data['message_id'] = str(message.id)
                                    await ws.send_json(data)
                    except Exception as e:
                        await self.bot.send_logs(e, traceback.format_exc(), more_info=msg)

        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(AtlantisBotApi(bot))
