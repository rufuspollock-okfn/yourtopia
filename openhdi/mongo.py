from pymongo import Connection as MongoConnection

conn = MongoConnection() 

def get_db():
    return conn['openhdi']


