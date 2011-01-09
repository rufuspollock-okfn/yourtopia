"""Model and 'business' logic.
"""
from random import choice, shuffle

from openhdi.mongo import get_db
from openhdi.importer import CATEGORIES

class Quiz(dict):
    def __init__(self, id_):
        db = get_db()
        quiz_data = db.quiz.find_one({'id': id_})
        assert quiz_data, '%s not found in db' % id_
        self.update(quiz_data)


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
        'questions': []
        }
    structures = []
    for dimension in [
        {'id': 'economy', 'label': 'Economy', 'set': 'hdi', 'proxy': 'NYGDPPCAPPPCD', 'color': '#e4adc5'},
        {'id': 'health', 'label': 'Health', 'set': 'hdi', 'proxy': 'SPDYNLE00IN', 'color': '#e4543a'},
        {'id': 'education', 'label': 'Education', 'set': 'hdi', 'proxy': 'SESECENRR', 'color': '#d9df29'},
        ]:
        dim_structure = list(db.indicator.find({'category.id': dimension['id'], 'select': True}))
        dimension['question'] = dimension['label']
        dimension['structure'] = dim_structure
        print ourquiz
        print dimension['id']
        structures.append(dimension)
        ourquiz['questions'] = ourquiz['questions'] + [x['id'] for x in dim_structure]
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

if __name__ == '__main__':
    import sys
    action = sys.argv[1]
    if action == 'delete':
        delete_all()
    elif action == 'load':
        load()
    elif action == 'quiz':
        setup_quiz()

