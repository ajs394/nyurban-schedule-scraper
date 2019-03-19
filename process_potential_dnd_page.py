from web_client import get_soup_from_url
from dnd_monster_dbo import monster, data_point
import progressbar

MONSTER_STATS = "MONSTER_STATS"
HAS_LINKS = "HAS_LINKS"
HAS_LINKS_AND_STATS = "HAS_LINKS_AND_STATS"
IRRELEVANT = ""


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
            links += [base_url + link['href']]
    
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

MONSTER_STAT_KEYWORDS = [
    "Challenge",
    "CR",
    "Hit Dice",
    "Hit Points", 
    "HP",
    "Armor Class", 
    "AC"
]

MONSTER_FULL_STAT_KEYWORDS = [
    "Actions",
    "Languages",
    "Saving",
    "Throws",
    "Skills",
    "STR",
    "DEX",
    "Speed",
    "alignment"
]

FEATURE_SET = list(set(MONSTER_STAT_KEYWORDS) | set(MONSTER_FULL_STAT_KEYWORDS))

def enrich_url_with_features(link):
    soup = get_soup_from_url(link)

    features = {}

    for feature in FEATURE_SET:
       features[feature] = len(soup.findAll(text = feature))

    return data_point(source_url=link, features=features)

def memoize(f):
    memo = {}
    def helper(x):
        if x not in memo:            
            memo[x] = f(x)
        return memo[x]
    return helper

def filter_link(link):
    return (link.has_attr('href') 
        and not link.endswith('.pdf'))

def classify_page(soup):
    is_monster_page = True
    for condition in MONSTER_STAT_KEYWORDS:
        has_condition = False
        for string in condition:
            has_condition = has_condition or soup.findAll(text = string)
        is_monster_page = is_monster_page and has_condition
    
    links = []
    for link in soup.findAll('a'):
        if filter_link(link):
            links += [link['href']]

    if links:
        for link in links:
            process_potential_dnd_page(link)
    if is_monster_page:
        return MONSTER_STATS
    return IRRELEVANT

def get_name_from_soup(soup):
    return

def process_monster_stats(soup):
    monster = monster()

    monster.name

    monster.save()

    return

@memoize
def process_potential_dnd_page(url):
    soup = get_soup_from_url(url)
    classification = classify_page(soup)
    switcher = {
        MONSTER_STATS: process_monster_stats(soup)
    }
    switcher.get(classification, "")

def retrieve_training_set():
    search_bestiary()
    search_monsterfinder()
    search_wikicreatures()
    search_wikilanguages()

if __name__ == '__main__':
    retrieve_training_set()