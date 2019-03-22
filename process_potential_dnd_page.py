import functools
import itertools
import random
import re
import string

import progressbar
from bs4.element import Comment

from data.dnd_monster_dbo import (data_point, full_page_data, monster,
                                  retreive_all_datapoints,
                                  retrieve_all_full_pages)
from data.features import (FEATURE_SET, MONSTER_STAT_KEYWORDS, NUM_UNIQUE,
                           PAGE_LENGTH, URL_CHARACTER_COUNTS,
                           WORD_COUNT_FEATURES)
from model.page_classifier_library import classify_page
from web_client import (get_content_from_url, get_soup_from_content,
                        get_soup_from_url, urljoin)

MONSTER_STATS = "MONSTER_STATS"
HAS_LINKS = "HAS_LINKS"
HAS_LINKS_AND_STATS = "HAS_LINKS_AND_STATS"
IRRELEVANT = ""

MAX_DEPTH = 5

monster_urls = []
other_urls = []

def add_dummy_empty_pages():
    size = len(retreive_all_datapoints())/10
    for _ in itertools.repeat(None, int(size)):
        dp = create_empty_data_point()
        dp.save()
        
def create_empty_data_point():
    features = {}

    for feature in FEATURE_SET:
       features[feature] = 0

    return data_point(source_url=''.join(random.choices(string.ascii_uppercase + string.digits, k=12)), features=features)

def data_from_cached_pages():
    print("retrieving pages from cache")
    bar = progressbar.ProgressBar(max_value=100)
    non_monster_base_urls = [
        "https://en.wikipedia.org"
    ]
    detailed_base_urls = [
        "http://chisaipete"
    ]
    # crapped out previous run, starting at last record processed
    pages = retrieve_all_full_pages()[3126:]
    count = 0
    for page in pages:
        is_monster = True
        is_detailed = False
        for base in non_monster_base_urls:
            if page.source_url.startswith(base):
                is_monster = False
        for base in detailed_base_urls:
            if page.source_url.startswith(base):
                is_detailed = True
                is_monster = True
        dp = enrich_full_page_with_features(page)
        dp.is_monster = is_monster
        dp.is_detailed = is_detailed
        dp.save()
        progress = count/len(pages)*100
        count += 1.0
        bar.update(progress)

def search_bestiary():
    print("retrieving bestiary pages: is_monster=True, is_detailed=True")
    bar = progressbar.ProgressBar(max_value=100) 
    base_url = 'http://chisaipete.github.io'
    soup = get_soup_from_url(base_url + '/bestiary/')

    links = []
    for link in soup.findAll('a'):
        if link.has_attr('href') and '/creatures' in link['href']:
            links += [base_url + link['href']]
    
    count = 0.0
    for link in links:
        try:
            dp = enrich_url_with_features(link)
        except:
            print("Continuing to next link")
            continue
        dp.is_monster = True
        dp.is_detailed = True
        dp.save()
        progress = count/len(links)*100
        count += 1.0
        bar.update(progress)

def search_monsterfinder():
    print("retrieving monsterfinder pages: is_monster=True, is_detailed=False")
    bar = progressbar.ProgressBar(max_value=100) 
    base_url = 'http://monsterfinder.dndrunde.de'
    soup = get_soup_from_url(base_url + '/allmonsters.php')

    links = []
    for link in soup.findAll('a'):
        if link.has_attr('href') and 'details' in link['href']:
            links += [urljoin(base_url, link['href'])]
    
    count = 0.0
    for link in links:
        try:
            dp = enrich_url_with_features(link)
        except:
            print("Continuing to next link")
            continue
        dp.is_monster = True
        dp.is_detailed = False
        dp.save()
        progress = count/len(links)*100
        count += 1.0
        bar.update(progress)

def search_wikicreatures():
    print("retrieving wikicreatures pages: is_monster=False, is_detailed=False")
    base_url = 'https://en.wikipedia.org'
    for letter in map(chr, range(65, 91)):
        print('Letter: {}'.format(letter))
        bar = progressbar.ProgressBar(max_value=100) 
        soup = get_soup_from_url(base_url + '/wiki/List_of_legendary_creatures_({})'.format(letter)) 
    
        creatures_ul = soup.find('div', class_='mw-parser-output').find('ul')

        links = []
        for li in creatures_ul.findAll('li'):
            link = li.find('a')
            if link.has_attr('href'):
                links += [base_url + link['href']]
        
        count = 0.0
        for link in links:
            dp = enrich_url_with_features(link)
            dp.save()
            progress = count/len(links)*100
            count += 1.0
            bar.update(progress)

def search_wikilanguages():
    print("retrieving wikilanguages pages: is_monster=False, is_detailed=False")
    bar = progressbar.ProgressBar(max_value=100) 
    base_url = 'https://en.wikipedia.org'
    soup = get_soup_from_url(base_url + '/wiki/List_of_language_names') 
    
    links = []
    for link in soup.findAll('a'):
        if link.has_attr('href') and '_language' in link['href']:
            links += [base_url + link['href']]
    
    count = 0.0
    for link in links:
        dp = enrich_url_with_features(link)
        dp.save()
        progress = count/len(links)*100
        count += 1.0
        bar.update(progress)

def enrich_full_page_with_features(full_page: full_page_data):
    soup = get_soup_from_content(full_page.page_data)
    return enrich_soup_with_features(soup, full_page.source_url)

def enrich_url_with_features(link):
    #return full_page_data(link, get_content_from_url(link).decode("utf-8"))
    soup = get_soup_from_url(link)
    return enrich_soup_with_features(soup, link)
    
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def get_all_visible_text(soup):
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def enrich_soup_with_features(soup, link):
    features = {}
    visible_text = get_all_visible_text(soup)

    for feature in WORD_COUNT_FEATURES:
       features[feature] = len(re.findall(feature, visible_text, re.IGNORECASE))

    for feature in URL_CHARACTER_COUNTS:
        features[feature] = link.count(feature)

    features[PAGE_LENGTH] = len(visible_text)
    unique = set()
    for word in visible_text.split():
        unique.add(word)
    features[NUM_UNIQUE] = len(unique)

    return data_point(source_url=link, features=features)

def memoize(func):
    cache = func.cache = {}
    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        key = args[0]
        if key not in cache:
            cache[key] = None
            func(*args, **kwargs)
        return cache[key]
    return memoized_func

def filter_link(link):
    return (link.has_attr('href') 
        and not link['href'].endswith('.pdf'))

def get_name_from_soup(soup):
    return

def process_monster_stats(soup):
    # monster = monster()

    # monster.name

    # monster.save()

    return

@memoize
def process_potential_dnd_page(url, depth):
    global MAX_DEPTH
    global monster_urls
    global other_urls
    if depth >= MAX_DEPTH:
        return
    print("Processing unique page {}".format(url))
    try:
        soup = get_soup_from_url(url)    
    except:
        print('Failed to access {}, proceeding'.format(url))
        return None

    links = []
    for link in soup.findAll('a'):
        if filter_link(link):
            links += [urljoin(url, link['href'])]

    if links:
        for link in links:
            process_potential_dnd_page(link, depth+1)
    
    dp: data_point = enrich_soup_with_features(soup, url)
    prediction = classify_page(dp)

    if prediction is not "Neither":
        monster_urls += [url]
        process_monster_stats(soup)
    else:
        other_urls += [url]

def retrieve_training_set(grab_fresh_data):
    if grab_fresh_data:
        search_monsterfinder()
        search_bestiary()
        search_wikicreatures()
        search_wikilanguages()
    else:
        data_from_cached_pages()
    #add_dummy_empty_pages()

if __name__ == '__main__':
    grab_fresh_data = False
    retrieve_training_set(grab_fresh_data)
