"""Model and 'business' logic.
"""
from random import choice, shuffle
import datetime

from openhdi.mongo import get_db
from openhdi.importer import CATEGORIES

class Quiz(dict):
    def __init__(self, id_):
        db = get_db()
        quiz_data = db.quiz.find_one({'id': id_})
        assert quiz_data, '%s not found in db' % id_
        self.update(quiz_data)

    @property
    def indicators(self):
        # assume depth 
        indicators = {}
        for dim in self['structure']:
            for ind in dim['structure']:
                indicators[ind['id']] = ind
        return indicators

class Weighting(dict):
    @classmethod
    def load(self, quiz_id, user_id, create=False):
        db = get_db()
        query = {'quiz_id': quiz_id, 'user_id': user_id} 
        w = db.weighting.find_one(query)
        if not w and create:
            return self.new(quiz_id, user_id)
        else:
            w = Weighting(w)
            return w

    def save(self):
        db = get_db()
        query = {'quiz_id': self['quiz_id'], 'user_id': self['user_id']} 
        db.weighting.update(query, self, upsert=True)

    @property
    def quiz(self):
        db = get_db()
        quiz = Quiz(self['quiz_id'])
        return quiz
    
    def compute_weights(self):
        indicator_ids = self.quiz['indicator_list']
        lookup = {}
        for name,qs in self['question_sets'].items():
            lookup[name] = {}
            for id_, weight in qs:
                lookup[name][id_] = weight

        weights = []
        for ind_id in indicator_ids:
            ind = self.quiz.indicators[ind_id]
            dim_id = ind['category']['id']
            dim_weight = lookup['__dimension__'][dim_id]
            ind_weight = lookup[dim_id][ind_id]
            weights.append(ind_weight*dim_weight)
        self['weights'] = weights

    @classmethod
    def new(self, quiz_id=None, user_id=None):
        '''New object'''
        w = Weighting({
            'quiz_id': None,
            'user_id' : None,
            # question sets done
            'sets_done': [],
            # answers keyed by question set ids
            # __dimension__ is special_
            # we use this so we can remember sets and order within sets
            # (so we can look at framing problems)
            'question_sets': {},
            # computed weight in same order as indicators on quiz
            'weights': [
            ]
        })
        w['quiz_id'] = quiz_id
        w['user_id'] = user_id
        w['created'] = datetime.datetime.now().isoformat()
        if not quiz_id:
            return
        quiz = w.quiz
        # assume for moment quiz structure has depth 2
        # TODO: randomize
        dims = quiz['structure']
        default_weight = float(1)/len(dims)
        w['question_sets']['__dimension__'] = [ [d['id'], default_weight] for d in
                dims ]
        for idx,dim in enumerate(quiz['structure']):
            indicators = dim['structure']
            def default_weight(ind):
                # assume only one proxy!
                if ind['id'] == dim['proxy']:
                    return 1
                else:
                    return 0
            w['question_sets'][dim['id']] = [ [ind['id'], default_weight(ind)] for ind in
                indicators ]
        w.compute_weights()
        return w

    
def get_questions(user_id):
    db = get_db()
    done = db.weighting.find({'user_id': user_id}).distinct('category')
    if not 'meta' in done:
        step = 1
        questions = []
        for id, data in CATEGORIES.items():
            if not data.get('set') == 'hdi': 
                continue
            questions.append({
                'id': id, 
                'label': data.get('label'),
                'question': data.get('label'),
                'category': {
                    'id': id,
                    'label': data.get('label'),
                    }
                })
    else:
        unanswered = [c for c, v in CATEGORIES.items() if c not in done and v.get('set') == 'hdi']
        step = 1 + 3 - len(unanswered)
        if not len(unanswered):
            return (step, [])
        questions = list(db.indicator.find({'category.id': choice(unanswered), 'select': True}))
    shuffle(questions)
    return (step, questions)


def validate_weight(key, value):
    db = get_db()
    if key not in CATEGORIES.keys():
        indicator = db.indicator.find_one({'id': key})
        if not indicator:
            abort(400)
        category = indicator.get('category').get('id')
    else: 
        category = 'meta'
    try: 
        weight = float(value)
        assert weight >=0.0, "Too small"
        assert weight <=100.0, "Too big"
    except Exception, e:
        abort(400)
    return (category, (key, weight))

def save_weightings(weightings, user_id):
    db = get_db()
    weighting = {'user_id': user_id}
    weights = [ validate_weight(d.get('id'),d.get('weighting'))
            for d in weightings
            ]
    items = [v for k,v in weights]
    weighting['items'] = items
    weighting['category'] = weights[0][0]
    weighting['indicators'] = dict(items).keys()
    db.weighting.update({'user_id': weighting.get('user_id'), 
                         'category': weighting.get('category')},
                         weighting, upsert=True)
    # TODO: reinstate update of aggregates?
    # aggregates.update(db, weighting)

def setup_quiz():
    db = get_db()
    ourquiz = {
        'id': 'yourtopia',
        'label': 'Yourtopia default quiz',
        'description': '',
        'structure': [],
        'indicator_list': []
        }
    structures = []
    for dimension in [
        {'id': 'economy', 'label': 'Economy', 'set': 'hdi', 'proxy': 'NYGNPPCAPPPCD', 'color': '#e4adc5'},
        {'id': 'health', 'label': 'Health', 'set': 'hdi', 'proxy': 'SPDYNLE00IN', 'color': '#e4543a'},
        {'id': 'education', 'label': 'Education', 'set': 'hdi', 'proxy': 'SESECENRR', 'color': '#d9df29'},
        ]:
        dim_structure = list(db.indicator.find({'category.id': dimension['id'], 'select': True}))
        dimension['question'] = dimension['label']
        dimension['structure'] = dim_structure
        structures.append(dimension)
        ourquiz['indicator_list'] = ourquiz['indicator_list'] + [x['id'] for x in dim_structure]
    ourquiz['structure'] = structures
    query = {'id': ourquiz['id']} 
    db.quiz.update(query, ourquiz, upsert=True)


def delete_all():
    db = get_db()
    for name in db.collection_names():
        if name not in ['system.indexes']:
            db.drop_collection(name)

def load():
    from openhdi import importer
    print 'Loading indicators'
    importer.load_indicator_from_file('data/indicator.csv')
    print 'Completed indicators'
    print 'Loading datasets'
    importer.load_dataset_from_file('data/dataset.csv')
    print 'Completed datasets'

    print 'Loading quiz'
    setup_quiz()
    print 'Completed quiz'

def interpolate_data():
    db = get_db()
    q = Quiz(u'yourtopia')    
    count = 0
    count2 = 0
    # 698 country indicator tuples with no data at all ...
    for indicator in q['indicator_list']:
        ind = db.indicator.find_one({'id': indicator})
        print ind['label']
        for country in db.datum.distinct('country'):
            time = '2007'
            # q = {'indicator_id': indicator, 'time': time}
            # q = {'indicator_id': indicator, 'country': country, 'time': {'$in':
            #     ['2007', '2006', '2005', '2004', '2003', '2002', '2001']}}
            q = {'indicator_id': indicator, 'country': country}
            found = sorted([[x['time'],x] for x in db.datum.find(q)])
            # if found == 0:
            #    count += 1
            if found:
                year = found[0][0]
                if year != '2007':
                    count += 1
                    newdata = dict(found[0][1])
                    del newdata['_id']
                    newdata['time'] = '2007'
                    newdata['interpolated'] = True
                    newq = dict(q)
                    newq['time'] = '2007'
                    db.datum.update(newq, newdata, upsert=True)
                # print ind['label'], country
            else:
                count2 += 1
    print db.datum.count()
    print count
    print count2


if __name__ == '__main__':
    import sys
    action = sys.argv[1]
    if action == 'delete':
        delete_all()
    elif action == 'load':
        load()
    elif action == 'interpolate':
        interpolate_data()
    elif action == 'quiz':
        setup_quiz()

