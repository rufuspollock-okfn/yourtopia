from pymongo import Connection as MongoConnection
from pymongo.dbref import DBRef

conn = MongoConnection() 

def get_db():
    return conn['openhdi']


