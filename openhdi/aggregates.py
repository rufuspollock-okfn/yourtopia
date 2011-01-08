from bson.code import Code
from mongo import get_db
from pprint import pprint
from json import dumps
from time import time

from importer import CATEGORIES

TIMES = ['2007']

# collection: datum 
# produce aggregates for each selected indicator
# cat, time, country, user -> weight, value
# ___, time, country, user -> weight, value 
map_datum_to_aggregates = """function() {
    var meta_weights = %(meta_weights)s;
    var d = this; 
    var w = %(weighting)s;
    w.items.forEach(function(i) {
        if (i[0] == d.indicator_id) {
            var value = (i[1]/100) * (meta_weights[w.category]/100) * d.normalized_value;
            emit({category: w.category, time: d.time, 
                  country: d.country, user_id: '%(user_id)s'},
                  value);
            emit({category: '__AXIS__', time: d.time,
                  country: d.country, user_id: '%(user_id)s'},
                  value); 
        }
    });}""" 

# collection: user_aggregates
# aggregate the per-user aggregates: 
# cat, time, country, ____ -> weight, value
# ___, time, country, ____ -> weight, value 
map_aggregates_to_aggregates = Code("""function() {
    emit({category: '__AXIS__', time: this._id.time,
          country: this._id.country, user_id: '__AXIS__'},
          this.value);
    emit({category: this._id.category, time: this._id.time, 
          country: this._id.country, user_id: '__AXIS__'},
          this.value);
}""")


# TODO: ask Guo about actual algorithm to be applied!  
reduce_aggregates = Code("""function(key, values) {
    var sum = 0; 
    values.forEach(function(v) { sum += v; });
    db.aggregates.update({"category" : key.category, 
                          "time" : key.time, 
                          "country" : key.country, 
                          "user_id" : key.user_id},
                          {'$set': {'value': sum}}, upsert=true); 
    return sum;
}""")

def create_fallbacks(db, user_id, items):
    # HACK
    items = dict(items)
    proxies = dict([(c.get('proxy'), k) for k, c in CATEGORIES.items() \
                    if k in items.keys() and c.get('is_hdi')])
    data = db.datum.find({'time': {'$in': TIMES},
                          'indicator_id': {'$in': proxies.keys()}})
    for datum in data:
        category = proxies.get(datum.get('indicator_id'))
        _id = {'category': category, 
               'time': datum.get('time'), 
               'country': datum.get('country'),
               'user_id': user_id}
        weight = items.get(category)/100
        value = weight * datum.get('normalized_value')
        db.aggregate.update({'_id': _id}, {'$set': {'value': value}}, upsert=True)

def update(db, weighting): 
    #t0 = time()
    user_id = weighting.get('user_id')
    if weighting.get('category') == 'meta': 
        create_fallbacks(db, user_id, weighting.get('items'))
        return
    meta_weights = {}
    meta = db.weighting.find_one({'category': 'meta', 'user_id': user_id})
    if not meta: 
        return
    for category, value in meta.get('items'):
        meta_weights[category] = value
    values = {'user_id': user_id,
              'weighting': dumps(weighting), 
              'meta_weights': dumps(meta_weights)}
    map_function = Code(map_datum_to_aggregates % values)
    res = db.datum.map_reduce(map_function, 
                              reduce_aggregates, 
                              query={'indicator_id': {'$in': weighting.get('indicators')}, 
                                     'time': {'$in': TIMES}})
    for result in res.find(): 
        db.aggregate.update({'_id': result.get('_id')}, result, upsert=True)
    #print "USER", time()-t0

def update_global(db):
    #t0 = time() 
    #  This can be done offline via CRON or something
    res = db.aggregate.map_reduce(map_aggregates_to_aggregates, 
                                   reduce_aggregates)
    for result in res.find():
        db.aggregate.update({'_id': result.get('_id')}, result, upsert=True)
    #print "GLOBAL", time()-t0


def get_weights(db): 
    return get_weights_by_user(db, '__AXIS__')

def get_weights_by_user(db, user_id):
    aggregates = db.aggregate.find({'_id.user_id': user_id})
    by_time = {}
    for aggregate in aggregates:
        _id = aggregate.get('_id')
        by_country = by_time.get(_id.get('time'), {})
        #by_category = by_country.get(_id.get('country'), {})
        #by_category[_id.get('category')] = aggregate.get('value')
        #by_country[_id.get('country')] = by_category
        by_country[_id.get('country')] = aggregate.get('value')
        by_time[_id.get('time')] = by_country
    return by_time



if __name__ == '__main__':
    db = get_db()
    ind = {'category': u'inequality',
           'indicators': [u'SIPOVGAP2', u'SPPOPDPND', u'SIPOVGINI', u'SIDST10TH10'],
           'items': [(u'SPPOPDPND', 15.0),
           (u'SIPOVGINI', 15.0),
           (u'SIPOVGAP2', 57.0),
           (u'SIDST10TH10', 15.0)],
             'user_id': u'fd35d20a-cbe4-41da-bcfd-5e4dae723a26'}
    update(db, ind) 
    update_global(db)
