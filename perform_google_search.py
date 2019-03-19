from googlesearch import search

from process_potential_dnd_page import process_potential_dnd_page

queries = [
    "dungeons and dragons monster stat blocks"
]

for query in queries:
    for url in search(query):
        process_potential_dnd_page(url)
