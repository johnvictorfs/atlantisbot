# Standard lib imports
import threading
import time

# Non-Standard lib imports
from discord.ext import commands
import discord
import schedule

# Local imports
import definesettings as setting


class RaidsNotifications:

    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def start_raids_notifications(self):
        channel = self.bot.get_channel(int(setting.RAIDS_NOTIF_CHAT_ID))
        await self.send_raids_message(channel)
        schedule.every(2).days.at("20:00").do(self.run_threaded, self.send_raids_message)

        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    async def run_threaded(task):
        task_thread = threading.Thread(target=task)
        task_thread.start()

    @staticmethod
    async def send_raids_message(channel):
            embed_title = "**Raids**"
            clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{setting.CLAN_NAME}/clanmotif.png"
            header_1 = f"Marque presença para os Raids de 21:00 no {setting.RAIDS_CHAT_ID}"
            header_1_value = "É necessário ter a tag @Raids, leia os tópicos fixados para saber como a obter."
            header_2 = "Não marque presença mais de uma vez."
            header_2_value = ""
            header_3 = f"Não mande mensagens desnecessários no {setting.RAIDS_CHAT_ID}."
            header_3_value = ""
            raids_notif_embed = discord.Embed(title=embed_title,
                                              description="",
                                              color=discord.Colour.dark_blue())
            raids_notif_embed.set_thumbnail(url=clan_banner_url)
            raids_notif_embed.add_field(name=header_1, value=header_1_value)
            raids_notif_embed.add_field(name=header_2, value=header_2_value)
            raids_notif_embed.add_field(name=header_3, value=header_3_value)
            await channel.send()


def setup(bot):
    bot.add_cog(RaidsNotifications(bot))
