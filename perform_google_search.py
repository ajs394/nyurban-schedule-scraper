from googlesearch import search

from process_potential_dnd_page import (monster_urls, other_urls,
                                        process_potential_dnd_page)

queries = [
    "dungeons and dragons monster stat blocks"
]

for query in queries:
    urls = search(query)
    for url in urls:
        process_potential_dnd_page(url, 0)
        print('{},{}'.format('url','is_monster'))
        for url in monster_urls:
            print('{},{}'.format(url,'TRUE'))
        for url in other_urls:
            print('{},{}'.format(url,'FALSE'))
