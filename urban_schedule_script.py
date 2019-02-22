import sys

from getopt import GetoptError, getopt

from urllib import parse
import bs4
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from requests.models import Response

from calendar_events import add_event, schedule_event

events = []
session = None
team_url_base = "https://www.nyurban.com/team-details/?team_id="

def nyurban_login(username, password):
    global session
    url = "https://www.nyurban.com/volleyball/"
    data = {'ny_username': username, 'ny_password':password}
    headers = {'accept-encoding': 'gzip, deflate, br', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'}

    session = requests.Session()

    r: Response = session.post(url, headers=headers, data=data)


def add_events(team_id):
    global events
    global session
    global team_url_base
    r = session.get(team_url_base + team_id)
    team_soup: BeautifulSoup = BeautifulSoup(r.content, 'lxml')

    team_name = team_soup.find("div", class_="team").find("span")

    team_table_divs: ResultSet = team_soup.find_all("div", class_="payMidWrapper team_div")
    # get all rows in table but skip header tr
    iter_trs = iter(team_table_divs[0].find_all("tr"))
    next(iter_trs) 
    for tr in iter_trs:
        if len( tr.find_parents("table")) > 1:
            continue
        tds = tr.find_all("td")
        correct_depth_tds = []
        for td in tds:
            if len( td.find_parents("table")) == 1:
                correct_depth_tds.append(td)
        date = correct_depth_tds[0].text
        time = correct_depth_tds[2].text
        if not time:
            continue
        address_url = correct_depth_tds[1].find("a").attrs['href']
        address = parse.parse_qs(parse.urlsplit(address_url).query)['address'][0]
        
        events.append(schedule_event(date=date,time=time,address=address,teamName=team_name.text))

def print_help():
    print("urban_schedule_script.py -u <username> -p <password> [-c <calendarName>] -t... <teamId>")
    print("\t-u --username")
    print("\t\tLogin name for nyurban website")
    print("\t-p --password")
    print("\t\tLogin password for nyurban website")
    print("\t-c --calendar\tDefault: primary")
    print("\t\tName (or 'summary') of Google Calendar")
    print("\t-t --team")
    print("\t\tList of team IDs to get data for from NYUrban website")
    print("\t-h --help")
    print("\t\tPrint this message")

def main(argv): 
    global events       
    teams = []
    username = ''
    password = ''
    calendar = 'primary'

    expected_args = [
        ["u:", "username="],#urban username
        ["p:", "password="],#urban password
        ["c:", "calendar="],#calendar name
        ["h", "help"],#help
        ["t:", "team="]#team ids
    ]
    chars = ""
    strs = []
    for expected in expected_args:
        chars += expected[0]
        strs += [expected[1]]
    
    try:
        opts, args = getopt(argv, chars, strs)
    except GetoptError:
        print_help()
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        if opt in ("-u", "--username"):
            username = arg
        if opt in ("-p", "--password"):
            password = arg
        if opt in ("-c", "--calendar"):
            calendar = arg
        if opt in ("-t", "--team"):
            teams += [arg]

    if not username:
        print('Username is a required argument, please supply your NYUrban username')
        print_help()
        sys.exit()
    if not password:
        print('Password is a required argument, please supply your NYUrban password')
        print_help()
        sys.exit()
    if len(teams) == 0:
        print('It is required to pass at least one NYUrban team ID (usually a 6 digit number found on your team page)')
        print_help()
        sys.exit()
    if not calendar:
        print('Calendar name not supplied, using default Google calendar')

    nyurban_login(username, password)

    for t in teams:
        add_events(t)

    for e in events:
        #add_event(e, "Katy and Alec's Calendar <3")
        add_event(e, calendar)

if __name__ == "__main__":
    main(sys.argv[1:])