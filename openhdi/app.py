"""The Flask App
"""
import os
from uuid import uuid4
from datetime import datetime

from flask import Flask, request, session, abort
from flaskext.genshi import Genshi, render_response

from openhdi.mongo import get_db, jsonify
import openhdi.model as model

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

@app.route('/api/profile', methods=['GET'])
def get_profile():
    db = get_db() 

# /api/weighting?NAME=[0.0...1.0]&NAME2=....
@app.route('/api/weighting', methods=['POST'])
def weighting():
    db = get_db()
    if not request.json or not isinstance(request.json, dict): 
        return jsonify(app, {'status': 'error', 
                             'message': 'No data given'})
    if not len(request.json.get('weightings')):
        return jsonify(app, {'status': 'ok', 'message': 'no data'})

    weighting = {}
    weights = [ model.validate_weight(d.get('id'),d.get('weighting'), db)
            for d in request.json.get('weightings')
            ]
    items = [v for k,v in weights]
    weighting['items'] = items
    weighting['category'] = weights[0][0]
    weighting['indicators'] = dict(items).keys()
    user_id = unicode(session.get('id'))
    db.user.update({'user_id': user_id}, 
                   {'$addToSet': {'weightings': weighting}},
                    upsert=True)
    return jsonify(app, {'status': 'ok', 'message': 'saved'})


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath( __file__ ))
    # parent directory
    config_path = os.path.join(os.path.dirname(here), 'openhdi.cfg')
    if 'OPENHDI_CONFIG' in os.environ:
        app.config.from_envvar('OPENHDI_CONFIG')
    elif os.path.exists(config_path):
        app.config.from_pyfile(config_path)

    app.run()

