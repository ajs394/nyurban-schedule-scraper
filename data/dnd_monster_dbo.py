from dataclasses import dataclass, asdict
from typing import Dict

from tinydb import Query, TinyDB

db = TinyDB('monsters.json')

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

def data_point_by_url(source_url):
    return data_point_from_record(
        retrieve_data_point(source_url)[0]
    )

def data_point_from_record(record):
        return data_point(source_url=record['source_url'],
            features=record['features'],
            is_monster=record['is_monster'],
            is_detailed=record['is_detailed'])

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
