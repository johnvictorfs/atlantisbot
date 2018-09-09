# DEPRECATED
# # Standard lib imports
# import threading
# import time
# import asyncio
#
# # Non-Standard lib imports
# from discord.ext import commands
# import discord
# import schedule
#
# # Local imports
# import definesettings as setting
#
#
# class RaidsNotifications:
#
#     def __init__(self, bot):
#         self.bot = bot
#
#     @commands.command(aliases=['start_raids_notif', 'raids_notifications_'])
#     async def start_raids_notifications(self, ctx, real="true"):
#         if real == "true":
#             channel = self.bot.get_channel(int(setting.RAIDS_NOTIF_CHAT_ID))
#         else:
#             channel = self.bot.get_channel(450059325810016267)
#         print(f"{ctx.author}: Started raids notifications.")
#         channel = self.bot.get_channel(int(setting.RAIDS_NOTIF_CHAT_ID))
#         # await self.send_raids_message(channel)
#         schedule.every(2).days.at("20:00").do(self.run_threaded, self.send_raids_message)
#         while True:
#             schedule.run_pending()
#             await asyncio.sleep(1)
#
#     @staticmethod
#     async def run_threaded(task):
#         task_thread = threading.Thread(target=task)
#         task_thread.start()
#
#     @staticmethod
#     async def send_raids_message(channel):
#             print(f"Sent raids notification in channel {channel}")
#             embed_title = "**Raids**"
#             clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{setting.CLAN_NAME}/clanmotif.png"
#             raids_notif_embed = discord.Embed(title=embed_title,
#                                               description="",
#                                               color=discord.Colour.dark_blue())
#             raids_notif_embed.set_thumbnail(url=clan_banner_url)
#             raids_notif_embed.add_field(
#                 name="Marque presença para os Raids de 21:00",
#                 value=f"{setting.RAIDS_CHAT_ID}\n"
#                       f"\n"
#                       f"É obrigatório ter a tag <@&376410304277512192> - Leia os tópicos fixos para saber como obter"
#                       f"\n\n"
#                       f"Não mande mensagens desnecessárias no {setting.RAIDS_CHAT_ID}\n"
#                       f"\n"
#                       f"Não marque presença mais de uma vez",
#                 inline=False)
#
#             await channel.send("<@&376410304277512192>")
#             await channel.send(embed=raids_notif_embed)
#
#
# def setup(bot):
#     bot.add_cog(RaidsNotifications(bot))
