"""The Flask App
"""
import os
from uuid import uuid4
from datetime import datetime

from flask import Flask, request, session, abort
from flaskext.genshi import Genshi, render_response
from flask import json

from openhdi.mongo import get_db, jsonify
import openhdi.model as model
import openhdi.aggregates as aggregates

app = Flask(__name__)
def configure_app():
    app.config.from_object('openhdi.settings_default')
    here = os.path.dirname(os.path.abspath( __file__ ))
    # parent directory
    config_path = os.path.join(os.path.dirname(here), 'openhdi.cfg')
    if 'OPENHDI_CONFIG' in os.environ:
        app.config.from_envvar('OPENHDI_CONFIG')
    elif os.path.exists(config_path):
        app.config.from_pyfile(config_path)
configure_app()

genshi = Genshi(app)
secret_key = app.config['SECRET_KEY']


@app.before_request
def make_session():
    if not 'id' in session:
        session['id'] = uuid4()


## ======================
## Routes and Controllers

@app.route('/')
def home():
    return render_response('index.html')

@app.route('/quiz')
def quiz():
    user_id = unicode(session.get('id'))
    questions = model.get_questions(user_id)
    return render_response(
        'quiz.html',
        dict(questions=questions)
        )

@app.route('/about')
def about():
    return render_response('about.html')

@app.route('/result')
def result():
    import iso3166
    db = get_db() 
    from aggregates import get_scores, get_scores_by_user
    user_scores = get_scores_by_user(db, unicode(session.get('id')))
    global_scores = get_scores(db)
    scores_data = json.dumps({
        'user': user_scores, 
        'global': global_scores
        })
    last_year='2007'
    def get_sorted(score_set):
        s = score_set[last_year]
        s = sorted(s.items(), cmp=lambda x,y: -cmp(x[1], y[1]))
        s = [ [x[0], x[1], iso3166.countries.get(x[0]).name] for x in s ]
        return s
    user_scores = get_sorted(user_scores)
    global_scores = get_sorted(global_scores)
    return render_response('result.html', dict(
        scores_data=scores_data,
        user_scores=user_scores,
        global_scores=global_scores
        ))


## -------------------------
## API

@app.route('/api/indicators')
def questions():
    user_id = unicode(session.get('id'))
    questions = model.get_questions(user_id)
    return jsonify(app, questions)

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    db = get_db()
    user_id = unicode(session.get('id'))
    if request.method == 'POST': 
        if not (request.form and 'label' in request.form):
            abort(400)
        db.user.update({'user_id': user_id}, 
                       {'$set': {'label': request.form.get('label')}}, upsert=True)
    user = db.user.find_one({'user_id': user_id})
    if not user:
        return jsonify(app, {})
    return jsonify(app, user)

@app.route('/api/reset', methods=['GET'])
def reset():
    db = get_db()
    user_id = unicode(session.get('id'))
    db.weighting.remove({'user_id': user_id})
    # could keep this as well 
    #db.user.remove({'user_id': user_id}) 
    #del session['id']
    return jsonify(app, {'status': 'ok'})

# /api/weighting?NAME=[0.0...1.0]&NAME2=....
@app.route('/api/weighting', methods=['POST'])
def weighting():
    db = get_db()
    if not request.json or not isinstance(request.json, dict): 
        return jsonify(app, {'status': 'error', 
                             'message': 'No data given'})
    if not len(request.json.get('weightings')):
        return jsonify(app, {'status': 'ok', 'message': 'no data'})
    
    weighting = {'user_id': unicode(session.get('id'))}
    weights = [ model.validate_weight(d.get('id'),d.get('weighting'), db)
            for d in request.json.get('weightings')
            ]
    items = [v for k,v in weights]
    weighting['items'] = items
    weighting['category'] = weights[0][0]
    weighting['indicators'] = dict(items).keys()
    db.weighting.update({'user_id': weighting.get('user_id'), 
                         'category': weighting.get('category')},
                         weighting, upsert=True)
    aggregates.update(db, weighting)
    return jsonify(app, {'status': 'ok', 'message': 'saved'})

@app.route('/api/scores')
def scores():
    db = get_db() 
    from aggregates import get_scores, get_scores_by_user
    data = {
        'user': get_scores_by_user(db, unicode(session.get('id'))),
        'global': get_scores(db)
        }
    return jsonify(app, data)



if __name__ == '__main__':

    app.run()

