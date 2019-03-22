from urllib import response
from urllib.parse import urljoin as urllib_urljoin

import requests
from bs4 import BeautifulSoup

session = None
headers = {'accept-encoding': 'gzip, deflate, br', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'}

def urljoin(base_url, relative_url):
    return urllib_urljoin(base_url, relative_url)

def start_session():
    global session

    session = requests.Session()

def get_content_from_url(url):
    global session
    global headers

    if not session:
        start_session()
    try:
        r: Response = session.get(url, headers=headers)
    except Exception as e:
        print("Exception handling request {}".format(url))
        raise(e)
    return r.content

def get_soup_from_content(content):
    return BeautifulSoup(content, 'lxml')

def get_soup_from_url(url):
    return get_soup_from_content(get_content_from_url(url))
