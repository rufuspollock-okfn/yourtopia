"""Model and 'business' logic.
"""
from random import choice, shuffle

from openhdi.mongo import get_db
from openhdi.importer import CATEGORIES

def get_questions(user_id):
    db = get_db()
    done = db.weighting.find({'user_id': user_id}).distinct('category')
    if not 'meta' in done:
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
        if not len(unanswered):
            return []
        questions = list(db.indicator.find({'category.id': choice(unanswered), 'select': True}))
    shuffle(questions)
    return questions

def get_weightings(user_id):
    pass


def validate_weight(key, value, db):
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
