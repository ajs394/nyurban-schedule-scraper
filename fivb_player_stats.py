import sys
from getopt import GetoptError, getopt
from urllib import parse

import bs4
import requests
import progressbar
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from pyparsing import originalTextFor
from requests.models import Response

players = []
session = None
fivb_url_base = "http://www.volleyball.world"
# bar = progressbar.ProgressBar(max_value=10)
bar = progressbar.ProgressBar(max_value=100) 
num_teams = 0

def start_session():
    global session

    session = requests.Session()

def get_team_urls():
    global session
    global fivb_url_base

    url = fivb_url_base + '/en/men/teams'

    headers = {'accept-encoding': 'gzip, deflate, br', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'}

    r: Response = session.get(url, headers=headers)
    
    teams_soup: BeautifulSoup = BeautifulSoup(r.content, 'lxml')

    teams_list = teams_soup.find("ul", class_="team-list").find("li").find("ul")

    team_table_links: ResultSet = teams_list.find_all("li")
    return_links = []
    for li in team_table_links:
        link = li.find("a")['href']
        return_links += [link + '/team_roster']
    return return_links

def add_players_from_team(team_url):
    global session
    global fivb_url_base
    global bar
    global num_teams
    url = fivb_url_base + team_url

    headers = {'accept-encoding': 'gzip, deflate, br', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'}

    r: Response = session.get(url, headers=headers)
    
    team_soup: BeautifulSoup = BeautifulSoup(r.content, 'lxml')

    roster_table = team_soup.find("section", class_="tabs-content").find("table")
    # get all rows in table but skip header tr
    tr_list = roster_table.find_all("tr")
    iter_trs = iter(tr_list)
    next(iter_trs) 
    num_players = len(tr_list)-1
    player_percent = 100/num_teams/num_players
    for tr in iter_trs:
        progress = min(100, bar.percentage + player_percent)
        bar.update(progress)
        tds = tr.find_all("td")
        add_player(tds)

def add_player(tds):
    global players
    player = lambda: None
    name_anchor = tds[1].find("a")
    player.name = name_anchor.text
    add_player_position(player, name_anchor['href'])
    player.birthday = tds[2].text
    player.height = tds[3].text
    player.weight = tds[4].text
    player.spike = tds[5].text
    player.block = tds[6].text
    players += [player]

def add_player_position(player, player_url):
    global session
    global fivb_url_base
    url = fivb_url_base + player_url

    headers = {'accept-encoding': 'gzip, deflate, br', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'}

    r: Response = session.get(url, headers=headers)
    
    player_soup: BeautifulSoup = BeautifulSoup(r.content, 'lxml')

    player.position = player_soup.find("span", class_="role").parent()[1].text.strip()

def main(argv): 
    global players
    global bar
    global num_teams

    start_session()

    team_urls = get_team_urls()
    num_teams = len(team_urls)
    
    bar.start()
    team_count=0
    for url in team_urls:
        progress = (100/num_teams)*team_count
        team_count += 1
        bar.update(progress)
        add_players_from_team(url)

    print("{},{},{},{},{},{},{}".format("name", "position", "birthday", "height", "weight", "spike", "block"))
    for player in players:
        print("{},{},{},{},{},{},{}".format(player.name, player.position, player.birthday, player.height, player.weight, player.spike, player.block))

if __name__ == "__main__":
    main(sys.argv[1:])
