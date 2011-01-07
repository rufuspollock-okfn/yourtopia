from flask import Flask, request, session, abort
from uuid import uuid4
from datetime import datetime
from flaskext.genshi import Genshi, render_response
from mongo import get_db, jsonify
from importer import CATEGORIES
from random import choice 
    
app = Flask(__name__)
app.secret_key = "harry" 
genshi = Genshi(app)


def get_questions():
    db = get_db()
    user_id = unicode(session.get('id'))
    done = db.user.find({'user_id': user_id}).distinct('weightings.category')
    if not 'meta' in done:
        questions = []
        for id, data in CATEGORIES.items():
            if not data.get('is_hdi'): 
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
        return questions
    unanswered = [c for c, v in CATEGORIES.items() if c not in done and v.get('is_hdi')]
    if not len(unanswered):
        return []
    return db.indicator.find({'category.id': choice(unanswered), 'select': True})


@app.before_request
def make_session():
    if not 'id' in session:
        session['id'] = uuid4()

@app.route('/api/indicators')
def questions():
    return jsonify(app, get_questions())

@app.route('/api/profile', methods=['GET'])
def get_profile():
    db = get_db() 
    

# /api/weighting?NAME=[0.0...1.0]&NAME2=....
@app.route('/api/weighting', methods=['POST'])
def submit():
    db = get_db()
    if not request.json or not isinstance(request.json, dict): 
        return jsonify(app, {'status': 'error', 
                             'message': 'No data given'})
    
    weighting = {}
    def validate_weight(key, value):
        if key not in CATEGORIES.keys():
            indicator = db.indicator.find_one({'id': key})
            if not indicator:
                abort(400)
            category = indicator.get('_category').get('id')
        else:
            category = 'meta'
        if '_category' in weighting and \
            weighting['_category'] != category:
            abort(400)
        weighting['_category'] = category
        try: 
            weight = float(value)
            assert weight >=0.0, "Too small"
            assert weight <=100.0, "Too big"
        except Exception, e:
            abort(400)
        return (key, weight)
    
    items = dict([validate_weight(k, v) for k,v \
        in request.json.items()])
    if sum(items.values()) > 101.0:
        abort(400)
    weighting.update(items)
    user_id = unicode(session.get('id'))
    db.user.update({'user_id': user_id}, 
                   {'$addToSet': {'weightings': weighting}},
                    upsert=True)
    return jsonify(app, {'status': 'ok', 'message': 'saved'})


@app.route('/')
def home():
    return render_response('index.html')

@app.route('/quiz')
def quiz():
    return render_response('quiz.html', dict(questions=get_questions()))

@app.route('/about')
def about():
    return render_response('about.html')

if __name__ == '__main__':
    app.run(debug=True)

