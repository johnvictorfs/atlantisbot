# Standard lib imports
from contextlib import closing
import codecs
import csv
import time

# Non-Standard lib imports
from discord.ext import commands
import discord
from bs4 import BeautifulSoup
import requests

# Local imports
import definesettings as setting

skill = {
    'attack': 'Ataque',
    'defence': 'Defesa',
    'strength': 'Força',
    'constitution': 'Constituição',
    'ranged': 'Combate á Distância',
    'prayer': 'Oração',
    'magic': 'Magia',
    'cooking': 'Culinária',
    'woodcutting': 'Corte de Lenha',
    'fletching': 'Arco e Flecha',
    'fishing': 'Pesca',
    'firemaking': 'Arte do Fogo',
    'crafting': 'Artesanato',
    'smithing': 'Metalurgia',
    'mining': 'Mineração',
    'herblore': 'Herbologia',
    'agility': 'Agilidade',
    'thieving': 'Roubo',
    'slayer': 'Extermínio',
    'farming': 'Agricultura',
    'runecrafting': 'Criação de Runas',
    'hunter': 'Caça',
    'construction': 'Construção',
    'summoning': 'Evocação',
    'dungeoneering': 'Dungeon',
    'divination': 'Divinação',
    'invention': 'Invenção',
    'overall': 'Total'
}

emoji = {
    'attack': '<:attack:499707565949583391>',
    'defence': '<:defence:499707566033600513>',
    'strength': '<:strength:499707566406762496>',
    'constitution': '<:constitution:499707566335459358>',
    'ranged': '<:ranged:499707566331527168>',
    'prayer': '<:prayer:499707566012497921>',
    'magic': '<:magic:499707566205566976>',
    'cooking': '<:cookingskill:499707566167687169>',
    'woodcutting': '<:woodcutting:499707566410956800>',
    'fletching': '<:fletching:499707566280933376>',
    'fishing': '<:fishing:499707566067286018>',
    'firemaking': '<:firemaking:499707566260224001>',
    'crafting': '<:crafting:499707566184726539>',
    'smithing': '<:smithing:499707566335459328>',
    'mining': '<:mining:499707566201503768>',
    'herblore': '<:herblore:499707566272544778>',
    'agility': '<:agility:499707566192984094>',
    'thieving': '<:thieving:499707566096646167>',
    'slayer': '<:slayer:499707566360625152>',
    'farming': '<:farming:499707566197047306>',
    'runecrafting': '<:runecrafting:499707566226669568>',
    'hunter': '<:hunter:499707566197047316>',
    'construction': '<:constructionskill:499707565949583361>',
    'summoning': '<:summoning:499707566335459368>',
    'dungeoneering': '<:dungeoneering:499707566268612619>',
    'divination': '<:divination:499707566348304404>',
    'invention': '<:invention:499707566419607552>',
    'overall': '<:skills_icon:499707566310293504>'
}


def translate(string):
    string = string.replace('hour', 'hora')
    string = string.replace('day', 'dia')
    string = string.replace('week', 'semana')
    if string == 'month':
        string = string.replace('month', 'mês')
    elif string == 'months':
        string = string.replace('months', 'meses')
    string = string.replace('to go', '')
    return string


def competition_details(name, comp_id):
    url = f"http://www.runeclan.com/clan/{name}/{comp_id}"

    source = requests.get(url).content

    soup = BeautifulSoup(source.decode('utf-8', 'ignore'), 'lxml')

    competition_table = soup.find('table',
                                  attrs={'class': 'regular', 'width': '100%', 'cellpadding': '0', 'cellspacing': '0'})

    players = []
    for comp in competition_table:
        try:
            comps = comp.find_all('td')
            competition = {
                'rank': comps[0].text,
                'name': comps[1].text,
                'exp_gained': comps[2].text,
            }
            players.append(competition)
        except IndexError:
            pass
    return players


def grab_competitions(content):
    soup = BeautifulSoup(content.decode('utf-8', 'ignore'), 'lxml')
    competitions_table = soup.find('table',
                                   attrs={'class': 'regular', 'width': '100%', 'cellpadding': '0', 'cellspacing': '0'})

    competitions = []
    for comp in competitions_table:
        try:
            comps = comp.find_all('td')
            link = comp.find('a', href=True)
            link = link['href']
            competition = {
                'name': comps[0].text.replace('&block; ', ''),
                'skill': comps[1].text,
                'start_date': comps[2].text,
                'duration': comps[3].text,
                'time_remaining': comps[4].text,
                'link': link
            }
            competitions.append(competition)
        except (TypeError, IndexError):
            pass
    return competitions


def get_competitions(clan):
    base_url = f"http://www.runeclan.com/clan/{clan}/"
    running_url = base_url + "competitions?view=1"
    finished_url = base_url + "competitions?view=2"

    running_source = requests.get(running_url).content
    finished_source = requests.get(finished_url).content

    running_competitions = grab_competitions(running_source)
    finished_competitions = grab_competitions(finished_source)

    soup = BeautifulSoup(running_source.decode('utf-8', 'ignore'), 'lxml')
    comp_count = soup.find('span', attrs={'class': 'events_comp_num', 'style': 'color:green;'})
    finished_count = soup.find('span', attrs={'class': 'events_comp_num', 'style': 'color:purple;'})

    competitions_dict = {
        'running_competitions_count': comp_count.text,
        'finished_competitions_count': finished_count.text,
        'running_competitions': running_competitions,
        'finished_competitions': finished_competitions,
    }
    return competitions_dict


class Competitions:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['comps', 'competitions', 'competicoes', 'running_comps', 'competicoes_ativas', 'comp'])
    async def running_competitions(self, ctx, index=0, players=10):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'running_competitions'.")
        start_time = time.time()
        competitions = get_competitions(setting.CLAN_NAME)
        if not competitions['running_competitions']:
            print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
            return await ctx.send("Nenhuma competição ativa no momento :(")
        if len(competitions['running_competitions']) > 1 and index is 0:
            competitions_embed = discord.Embed(
                title="Competições Ativas",
                description=f"" + ("_\\" * 15) + "_",
                color=discord.Colour.dark_red(),
                url=f"http://www.runeclan.com/clan/{setting.CLAN_NAME}/competitions")
            index = 0
            for comp in competitions['running_competitions']:
                field_value = f"{emoji[comp['skill'].lower()]} " \
                              f"{skill[comp['skill'].lower()]}\n" \
                              f"__Duração__: {translate(comp['duration'])}\n"

                if comp['start_date'] == 'active':
                    field_value += f"__Tempo Restante__: {translate(comp['time_remaining'])}"
                else:
                    field_value += f"__Início daqui a__: {translate(comp['start_date'])}"
                field_value += "\n"
                field_value += ("_\\" * 15) + "_"
                competitions_embed.add_field(name=f"#{index + 1} - {comp['name']}",
                                             value=field_value,
                                             inline=False)
                index += 1
            print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
            return await ctx.send(
                content=f"Há mais de uma competição ativa no momento\n"
                        f"Selecione uma utilizando:\n`{setting.PREFIX}comp <número da competição> "
                        f"<número de jogadores (padrão = 10)>`",
                embed=competitions_embed)
        else:
            if len(competitions['running_competitions']) is 1:
                index = 1
            try:
                competition = competitions['running_competitions'][index - 1]
            except IndexError:
                await ctx.send(f"Você tentou acessar a competição número {index}, "
                               f"mas o número de competições ativa no momento é "
                               f"{len(competitions['running_competitions'])}.")
                print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
                return
            comp_embed = discord.Embed(
                title=competition['name'],
                description=f"{emoji[competition['skill'].lower()]} "
                            f"{skill[competition['skill'].lower()]}",
                color=discord.Colour.blue(),
                url=f"http://www.runeclan.com/clan/{setting.CLAN_NAME}/{competition['link']}")
            comp_embed.add_field(name="__Duração Total__",
                                 value=f"{translate(competition['duration'])}",
                                 inline=False)
            if competition['start_date'] == 'active':
                comp_details = competition_details(setting.CLAN_NAME, competition['link'])
                comp_embed.add_field(name="__Tempo Restante__",
                                     value=f"{translate(competition['time_remaining'])}\n" + ("_\\" * 15) + "_",
                                     inline=False)
                for i in range(players):
                    if int(comp_details[i]['exp_gained'].replace(',', '')) > 0:
                        comp_embed.add_field(name=f"__#{i + 1}__ - {comp_details[i]['name']}",
                                             value=f"**Exp:** {comp_details[i]['exp_gained']}\n" + ("_\\" * 15) + "_",
                                             inline=False)
            else:
                comp_embed.add_field(name=f"__Início daqui a__",
                                     value=f"{translate(competition['start_date'])}",
                                     inline=False)
            print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
            return await ctx.send(content=None, embed=comp_embed)

    @commands.command(aliases=['pontos', 'comppontos', 'compontos', 'pcomp', 'comptab', 'comptable', 'compranks', 'comp_points', 'compp', 'compps'])
    async def comp_pontos(self, ctx, number=10):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'comp_pontos'.")
        start_time = time.time()
        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTkyylgIdAOZ21UOeOAyGz5FPuvg9eqD1nvG6i8dBc2eD9LCjqqnW0VBRwZ8j5Kybppn3q_hfOldjFj/pub?gid=0&single=true&output=csv'
        with closing(requests.get(url, stream=True)) as r:
            if r.status_code != 200:
                return await ctx.send("Houve um erro tentando pegar as informações dessa competição, tente novamente mais tarde :(")
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=',', quotechar='"')
            if not reader:
                print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
                return await ctx.send(f'Nenhuma competição fazendo uso do sistema de pontos no momento. tente o comando `{setting.PREFIX}comp` para ver outras competições')
            list_reader = list(reader)
            raw_skill = list_reader[0][0].lower()
            skill_ = skill[raw_skill]
            finished_days = int(list_reader[0][1])
            remaining_days = int(list_reader[0][2])
            comp_embed = discord.Embed(
                title="__Competição de Pontos__",
                description=f"{emoji[raw_skill]} {skill_}\n__Dias Finalizados:__ {finished_days}\n__Dias Restantes:__ {remaining_days}\n" + ("_\\" * 15) + "_",
                color=discord.Colour.dark_red(),
                url=f"https://docs.google.com/spreadsheets/d/e/2PACX-1vRS1xBkGJi6G5utxcbHJRkKxum2qmcKdvLv7A-O4bFKvnujF_pOSK0tps5gZU1MjSkIbEY-Bup5fJDm/pubhtml#")
            i = 1
            for player in list_reader[1:]:
                comp_embed.add_field(
                    name=f"__#{i}__ - {player[0]}",
                    value=f"**Pontos:** {player[2]}\n**Exp (Total top 10s):** {int(player[1]):,}\n" + ("_\\" * 15) + "_",
                    inline=False)
                i += 1
                if i > number:
                    break
            print(f"    - Answer sent. Took {time.time() - start_time:.4f}s")
            return await ctx.send(embed=comp_embed)


def setup(bot):
    bot.add_cog(Competitions(bot))
