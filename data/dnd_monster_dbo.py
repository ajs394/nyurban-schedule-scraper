import os
from dataclasses import asdict, dataclass
from typing import Dict

from tinydb import Query, TinyDB

from constants.data import db_name, full_data_db_name

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../data/{}.json'.format(db_name))
full_data_filename = os.path.join(dirname, '../data/{}.json'.format(full_data_db_name))
db = TinyDB(filename)
full_data_db = None
def get_full_data_db():
    global full_data_db
    if full_data_db is None:
        full_data_db = TinyDB(full_data_filename)
    return full_data_db

@dataclass
class monster:
    name: str
    version: str
    source: str = ""
    cr: str = ""
    plane: str = ""

    def save(self):
        insert_monster(asdict(self))
    
    

@dataclass
class data_point:
    source_url: str
    features: Dict[str, str]
    is_monster: bool = False
    is_detailed: bool = False

    def save(self):
        insert_data_point(asdict(self))

@dataclass
class full_page_data:
    source_url: str
    page_data : str

    def save(self):
        insert_full_page(asdict(self))

def data_point_by_url(source_url):
    return data_point_from_record(
        retrieve_data_point(source_url)[0]
    )

def full_page_data_from_record(record):
    return full_page_data(source_url=record['source_url'],
        page_data=record['page_data'])

def data_point_from_record(record):
    return data_point(source_url=record['source_url'],
        features=record['features'],
        is_monster=record['is_monster'],
        is_detailed=record['is_detailed'])

def insert_full_page(full_page_data: full_page_data):
    get_full_data_db().table('full_pages').insert(full_page_data)

def insert_monster(monster: monster):
    global db
    db.table('monster').insert(monster)

def insert_data_point(dp: data_point):
    global db
    db.table('data').insert(dp)

def retrieve_monster(name: str, version: str):
    global db
    Monster = Query()
    return db.table('monster').search((Monster.name == name) & (Monster.version == version))

def retrieve_data_point(source_url: str):
    global db
    Data_point = Query()
    return db.table('data').search(Data_point.source_url == source_url)

def retreive_all_datapoints():
    return db.table('data').all()

def retrieve_all_full_pages():
    return [full_page_data_from_record(x) for x in get_full_data_db().table('full_pages').all()]

# TODO: implement batching
def run_map_on_full_pages(func):
    get_full_data_db().table('full_pages').process_elements(func)
