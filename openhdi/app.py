"""The Flask App
"""
import os
from uuid import uuid4
from datetime import datetime

from flask import Flask, request, session, abort
from flaskext.genshi import Genshi, render_response

from openhdi.mongo import get_db, jsonify
import openhdi.model as model
import openhdi.aggregates as aggregates

app = Flask(__name__)
app.config.from_object('openhdi.settings_default')

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
        if not (request.json and 'label' in request.json):
            abort(400)
        db.user.update({'user_id': user_id}, 
                       {'$set': {'label': request.json.get('label')}}, upsert=True)
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
    from pprint import pprint 
    pprint(weighting)
    aggregates.update(db, weighting)
    return jsonify(app, {'status': 'ok', 'message': 'saved'})

@app.route('/api/scores')
def scores():
    db = get_db() 
    from aggregates import get_weights, get_weights_by_user
    data = {
        'user': get_weights_by_user(db, unicode(session.get('id'))),
        'global': get_weights(db)
        }
    return jsonify(app, data)



if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath( __file__ ))
    # parent directory
    config_path = os.path.join(os.path.dirname(here), 'openhdi.cfg')
    if 'OPENHDI_CONFIG' in os.environ:
        app.config.from_envvar('OPENHDI_CONFIG')
    elif os.path.exists(config_path):
        app.config.from_pyfile(config_path)

    app.run()

