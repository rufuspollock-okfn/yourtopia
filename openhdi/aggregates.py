from bson.code import Code
from mongo import get_db
from pprint import pprint
from json import dumps
from time import time
from colors import color_range

from importer import CATEGORIES
import openhdi.model as model

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
    return sum/Math.max(1, values.length);
}""")


map_weightings = Code("""function() {
    if (this.user_id != '__AXIS__') {
        var ind = this.indicators; 
        ind.sort(); 
        emit({indicators: ind, category: this.category},
             this.items);
    }
}""")

reduce_weightings = Code("""function (key, values) {
    var sums = new Object();
    values.forEach(function(items) {
        items.forEach(function(item) {
            k = item[0];
            if (!sums[k]) sums[k] = 0;
            sums[k] += item[1];
        }); 
    });
    var means = new Object();
    for (var k in sums) {
         means[k] = sums[k]/Math.max(1, values.length); 
    }
    return means; 
}""")


def create_fallbacks(db, user_id, items):
    # HACK
    items = dict(items)
    proxies = dict([(c.get('proxy'), k) for k, c in CATEGORIES.items() \
                    if k in items.keys() and c.get('set') == 'hdi'])
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
    #res = db.aggregate.map_reduce(map_aggregates_to_aggregates, 
    #                               reduce_aggregates)
    #for result in res.find():
    #    db.aggregate.update({'_id': result.get('_id')}, result, upsert=True)
    #print "GLOBAL", time()-t0

    res = db.weighting.map_reduce(map_weightings, reduce_weightings)
    for result in res.find():
        db.weighting.update({'user_id': '__AXIS__', 
                             'category': result.get('_id').get('category'),
                             'indicators': result.get('_id').get('indicators')}, 
                            {'$set': {'items': result.get('value').items()}}, upsert=True)


def get_scores(db): 
    return get_scores_by_user(db, '__AXIS__')

def get_scores_by_user(db, user_id):
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

class Aggregator(object):
    def __init__(self):
        self.db = get_db()
        self.quiz = model.Quiz(u'yourtopia')
        self.country_list = self.db.datum.distinct('country')

    def _query(self, user_id):
        return dict(quiz_id=self.quiz['id'], user_id=user_id)

    def compute(self, user_id):
        # order matters!
        self.compute_user_score(user_id)
        self.compute_average_weighting()
        self.compute_user_score()

    def compute_all(self):
        for user_id in self.db.weighting.distinct('user_id'):
            self.compute_user_score(user_id)
        self.compute_average_weighting()
        self.compute_user_score()

    def compute_average_weighting(self):
        db = self.db
        avg = model.Weighting.new(quiz_id=self.quiz['id'], user_id='__AVG__')
        q = {'quiz_id': self.quiz['id']}
        count = 0
        weightsum = [0] * len(self.quiz['indicator_list'])
        for weighting in db.weighting.find(q):
            for idx, weight in enumerate(weighting['weights']):
                weightsum[idx] = weightsum[idx] + weight 
            count += 1
        avg['weights'] = [ x/float(max(1,count)) for x in weightsum ]
        avg['count'] = count
        avg.save()
        return avg
    
    def weights(self, user_id='__AVG__'): 
        return dict(
            zip(self.quiz['indicator_list'],
                self.db.weighting.find_one(self._query(user_id))['weights']
                )
            )

    def scores(self, user_id='__AVG__', year='2007'):
        q = self._query(user_id)
        q['time'] = year
        out = [ [x['country'], x['score']] for x in
            self.db.aggregate.find(q) ]
        return out

    def compute_average_score(self, year='2007'):
        '''Don't need this with average weightings!'''
        q = self._query('__AVG__')
        q['time'] = year
        for country in self.country_list:
            q['country'] = country
            avg = dict(q)
            user_scores_q = dict(q)
            user_scores_q['user_id'] = {'$ne': '__AVG__'}
            count = 0
            oursum = 0
            for score in self.db.aggregate.find(user_scores_q):
                count += 1
                oursum += score['score']
            avg['score'] = oursum / count
            self.db.aggregate.update(q, avg, upsert=True)

    def compute_user_score(self, user_id='__AVG__', year='2007'):
        weights = self.weights(user_id)
        # db.datum.find({'time': year}) 
        for country in self.country_list:
            oursum = 0
            for indicator_id in self.quiz['indicator_list']:
                w = weights[indicator_id] 
                if not w > 0:
                    continue
                # indicator = self.db.indicator.find_one({'id': indicator_id})
                val = self.db.datum.find_one({
                        'time': year,
                        'country': country,
                        'indicator_id': indicator_id
                        })
                if val is None: # missing value
                    val = self.db.datum.find_one({
                            'country': country,
                            'indicator_id': indicator_id
                            })
                if val is None:
                    # ignore this indicator!
                    continue
                    # val = {'normalized_value': 0.2}
                    # oursum = 0
                    # break
                oursum += w * val['normalized_value']
            score = {'score': oursum/len(self.quiz['indicator_list'])}
            q = self._query(user_id)
            q['country'] = country
            q['time'] = year
            score.update(q)
            self.db.aggregate.update(q, score, upsert=True)

if __name__ == '__main__':
    db = get_db()
    ind = {'category': u'inequality',
           'indicators': [u'SIPOVGAP2', u'SPPOPDPND', u'SIPOVGINI', u'SIDST10TH10'],
           'items': [(u'SPPOPDPND', 15.0),
           (u'SIPOVGINI', 15.0),
           (u'SIPOVGAP2', 57.0),
           (u'SIDST10TH10', 15.0)],
             'user_id': u'fd35d20a-cbe4-41da-bcfd-5e4dae723a26'}
    #update(db, ind) 
    update_global(db)
    #pprint(get_weightings(db))
