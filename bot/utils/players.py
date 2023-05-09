from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import asyncio
import aiohttp

from io import StringIO
from typing import List
import json

try:
    with open("bot/data/skills.json") as f:
        skills = json.load(f)

    with open("bot/data/activities.json") as f:
        activities = json.load(f)
except FileNotFoundError:
    with open("../data/skills.json") as f:
        skills = json.load(f)

    with open("../data/activities.json") as f:
        activities = json.load(f)


async def get_player_df_runeclan(player_name: str) -> pd.DataFrame:
    name = player_name.replace(" ", "_")
    url = f"http://www.runeclan.com/user/{name}"

    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            text = await r.text()

    soup = BeautifulSoup(text, "lxml")

    table = soup.find("table", attrs={"class": "regular"})

    headers = [header.text for header in table.find_all("th")]
    value_headers = ["Skill", "Level", "XP", "RS Rank"]

    player_skills = [
        {
            headers[i]: cell.text
            for i, cell in enumerate(row.find_all("td"))
            if headers[i] in value_headers
        }
        for row in table.find_all("tr")
    ][1:]

    # Rename RuneClan Headers
    new_value_headers = {
        "Skill": "Name",
        "Level": "Level",
        "XP": "Exp",
        "RS Rank": "Rank",
    }

    player_skills = [
        {new_value_headers[key]: value.replace(",", "") for key, value in skill.items()}
        for skill in player_skills
    ]

    df = pd.DataFrame(player_skills)

    df["Level"] = df["Level"].astype(int, errors="ignore")
    df["Exp"] = df["Exp"].astype(int, errors="ignore")
    df["Rank"] = df["Rank"].astype(int, errors="ignore")

    return df


async def get_player_df_api(player_name: str) -> pd.DataFrame:
    name = player_name.replace(" ", "_")
    url = f"https://secure.runescape.com/m=hiscore/index_lite.ws?player={name}"

    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            text = await r.text()

    data = StringIO(text)
    df = pd.read_csv(data, header=None, names=["Rank", "Level", "Exp"])

    # Convert number fields to int
    df = df.astype(int, errors="ignore")

    # Switch negative values to 0
    df_nums = df._get_numeric_data()
    df_nums[df_nums < 0] = 0

    # Set Name field values
    names = skills + activities
    df["Name"] = names

    return df


def get_skills_df(df: pd.DataFrame, skills: List[str]) -> pd.DataFrame:
    """
    Gets a player's skills in a DataFrame
    """
    skills_df = pd.DataFrame()

    for index, row in df.iterrows():
        if row["Name"] in skills:
            skills_df = skills_df.append(row)

    return skills_df.astype(int, errors="ignore")


def compare_players(before: pd.DataFrame, after: pd.DataFrame) -> float:
    # Player's Exp in a skill can't have decreased
    # unless in exceptional cases (exp loss by ban or skill resets)
    # so those are being ignored for now
    new_df = pd.DataFrame()

    new_df["isLower"] = np.where(before["Exp"] > after["Exp"], "y", "n")
    if "y" in new_df["isLower"].values:
        # 0% percent chance
        return 0

    new_df["differentExp"] = np.where(before["Exp"] != after["Exp"], "n", "y")
    if "n" not in new_df["differentExp"].values:
        # No difference in all exp values
        return 100

    new_df["differenceExp"] = after["Exp"] - before["Exp"]

    # Amount of skills that have a difference between the two DFs of over a certain amount
    big_difference = np.sum(new_df["differenceExp"] < 4_000_000)

    # Includes Overall Exp as 'skill'
    max_skills = len(skills)

    return (big_difference / max_skills) * 100


if __name__ == "__main__":
    import sys

    before = asyncio.run(
        get_player_df_runeclan(sys.argv[1].replace('"', "").replace("'", ""))
    )
    after = asyncio.run(
        get_player_df_runeclan(sys.argv[2].replace('"', "").replace("'", ""))
    )

    print(compare_players(before, after))
