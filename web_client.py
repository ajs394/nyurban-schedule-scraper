from urllib import response

import requests
from bs4 import BeautifulSoup

session = None
headers = {'accept-encoding': 'gzip, deflate, br', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'}

def start_session():
    global session

    session = requests.Session()

def get_soup_from_url(url):
    global session
    global headers

    if not session:
        start_session()
    try:
        r: Response = session.get(url, headers=headers)
    except Exception as e:
        print("Exception handling request {}".format(url))
        raise(e)
    return BeautifulSoup(r.content, 'lxml')
