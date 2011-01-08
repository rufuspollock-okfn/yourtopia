from pymongo import Connection as MongoConnection
from pymongo.dbref import DBRef
from pymongo.objectid import ObjectId
from pymongo.cursor import Cursor
from datetime import datetime, date
from json import JSONEncoder 

class MongoEncoder(JSONEncoder):
    
    def default(self, o):
        if isinstance(o, Cursor):
            return [x for x in o]
        if isinstance(o, DBRef):
            return o.as_doc().to_dict()
        elif isinstance(o, ObjectId):
            return unicode(o)
        elif isinstance(o, (datetime, date)):
            return o.isoformat()
        return JSONEncoder.default(self, o)

def jsonify(app, obj):
    from flask import request
    content = MongoEncoder().encode(obj) 
    if 'callback' in request.args:
        content = str(callback) + '(' + content+ ')'
    return app.response_class(content, mimetype='application/json')


def get_db():
    from openhdi.app import app
    conn = MongoConnection(
       app.config['MONGODB_HOST'],
       app.config['MONGODB_PORT'],
       pool_size=app.config['MONGODB_POOL_SIZE']
       )
    dbname = app.config.get('MONGODB_DATABASE')
    db = conn[dbname]
    # auth = db.authenticate(db_info['username'], db_info['password'])
    # if not auth:
    #    raise Exception('Authentication to MongoDB failed')
    return db

