from dataclasses import dataclass
from typing import List, Dict

from discord.ext import commands
from bs4 import BeautifulSoup
import bs4
import discord

from bot.bot_client import Bot
from bot.utils.context import Context


@dataclass
class PlayerData:
    rank: int
    name: str
    exp_gained: int


@dataclass
class ExpTracker:
    total_exp: int
    players: List[PlayerData]


class RuneclanTracker(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_unload(self):
        pass

    def format_tracker(self, data: str) -> ExpTracker:
        soup = BeautifulSoup(data, "lxml")

        attrs: Dict[str, str] = {
            "class": "regular",
            "width": "100%",
            "cellpadding": "0",
            "cellspacing": "0",
        }
        tracker_table = soup.find("table", attrs=attrs)

        players: List[PlayerData] = []
        total_exp: int = 0

        for player in tracker_table:
            tds: List[bs4.element.Tag] = player.find_all("td")

            if len(tds) < 3:
                continue

            rank, name, exp_gained, *rest = tds

            exp_gained = int(exp_gained.text.replace(",", ""))

            if name.text == "Clan Total":
                total_exp = exp_gained
                continue

            player_data = PlayerData(int(rank.text), name.text, exp_gained)

            players.append(player_data)

        return ExpTracker(total_exp, players)

    @commands.command("tracker", aliases=["exptracker", "hiscores"])
    async def exp_tracker(
        self,
        ctx: Context,
        inicio: str,
        fim: str,
        habilidade: str = "geral",
        quantidade: int = 10,
    ):
        skills = {
            "geral": {"id": 2, "emoji": "<:overall_skill:647655515266088986>"},
            "ataque": {"id": 3, "emoji": "<:attack:499707565949583391>"},
        }

        skill = skills.get(habilidade.lower())

        if not skill:
            skill_options = ""
            for skill_name, skill_value in skills.items():
                skill_options += f'{skill_value["emoji"]} **{skill_name.title()}**\n'

            return await ctx.send(
                f"Habilidade '{habilidade}' não encontrada. Opções:\n\n{skill_options}"
            )

        url: str = (
            f'http://www.runeclan.com/clan/Atlantis/xp-tracker?skill={skill["id"]}'
        )

        payload: Dict[str, str] = {
            "criteria_set1": "custom",
            "criteria1_date1_submit": inicio,
            "criteria1_date2_submit": fim,
            "search_gains": "Search Gains",
            "criteria_set2": "yesterday",
            "criteria2_date1": "",
            "criteria2_date1_submit": "",
            "criteria2_date2": "",
            "criteria2_date2_submit": "",
            "criteria_set3": "week",
            "criteria3_date1": "",
            "criteria3_date1_submit": "",
            "criteria3_date2": "",
            "criteria3_date2_submit": "",
        }

        request = await self.bot.post_data(url, payload)
        data = await request.text()

        tracker = self.format_tracker(data)

        skill_display = f"{habilidade.title()} {skill['emoji']}"

        embed = discord.Embed(
            title=f"__Ranking de Exp__ (**{inicio}** - **{fim}**)",
            description=f"**Exp Total:** {tracker.total_exp:,}\n**Habilidade:** {skill_display}",
            color=discord.Color.blurple(),
        )

        embed.set_thumbnail(
            url=f"http://services.runescape.com/m=avatar-rs/{self.bot.setting.clan_name}/clanmotif.png"
        )

        for player in tracker.players[:quantidade]:
            embed.add_field(
                name=f"__**#{player.rank}**__ - {player.name}",
                value=f"{player.exp_gained:,}",
                inline=False,
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RuneclanTracker(bot))
