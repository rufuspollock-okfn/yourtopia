"""The Flask App
"""
import os
from uuid import uuid4
from datetime import datetime

from flask import Flask, request, session, abort, redirect, g, url_for, flash
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
QUIZ = app.config['QUIZ']

@app.before_request
def make_session():
    if not 'id' in session:
        session['id'] = str(uuid4())
    g.user_id = session.get('id') 


## ======================
## Routes and Controllers

@app.route('/')
def home():
    return render_response('index.html')

@app.route('/quiz')
def quiz():
    # step = int(request.args.get('stage', '1'))
    quiz = model.Quiz(QUIZ)
    w = model.Weighting.load(QUIZ, g.user_id, create=True)
    step = len(w['sets_done']) + 1
    if step == 4:
        agg = aggregates.Aggregator()
        agg.compute_user_score(g.user_id)
        agg.compute_average_weighting()
        agg.compute_user_score()
        # agg.compute_average_score()
        return redirect(url_for('result_me'))
    elif step == 1:
        dimension = '__dimension__'
        questions = quiz['structure']
    else:
        # use order of dimensions in quiz
        dimension = quiz['structure'][step-1]['id']
        questions = quiz['structure'][step-1]['structure']
    return render_response('quiz.html', dict(
        questions=questions,
        step=step,
        dimension=dimension
        ))

@app.route('/quiz', methods=['POST'])
def quiz_submit():
    def indicator(field_name):
        return field_name.split('-')[1]
    weightings = [
            [indicator(x[0]), int(x[1])/float(100)]
            for x in request.form.items()
            if x[0].startswith('weighting-')
            ]
    dimension = request.form['dimension']
    # TODO: should be stricter about it existing already
    w = model.Weighting.load(QUIZ, g.user_id, create=True)
    w['question_sets'][dimension] = weightings
    w['sets_done'].append(dimension)
    w.compute_weights()
    w.save()
    flash('Saved your weightings')
    return quiz()

@app.route('/about')
def about():
    return render_response('about.html')

@app.route('/how')
def how():
    return render_response('how.html')

@app.route('/result')
def result():
    import iso3166
    agg = aggregates.Aggregator()
    user_scores = agg.scores(g.user_id)
    global_scores = agg.scores()
    scores_data = json.dumps({
        'user': user_scores, 
        'global': global_scores
        })
    # last_year='2007'
    def get_sorted(score_set):
        s = score_set
        s = sorted(s, cmp=lambda x,y: -cmp(x[1], y[1]))
        s = [ [x[0], x[1], iso3166.countries.get(x[0]).name] for x in s ]
        return s
    user_scores = get_sorted(user_scores)
    global_scores = get_sorted(global_scores)
    return render_response('result.html', dict(
        scores_data=scores_data,
        user_scores=user_scores,
        global_scores=global_scores
        ))

@app.route('/result/me')
def result_me():
    import iso3166
    agg = aggregates.Aggregator()
    user_scores = agg.scores(g.user_id)
    global_scores = agg.scores()
    def get_sorted(score_set):
        s = score_set
        s = sorted(s, cmp=lambda x,y: -cmp(x[1], y[1]))
        # normalize too (avoid divide by 0)
        ourmax = max(0.00000000001, s[0][1])
        s = [ [x[0], x[1]/ourmax, iso3166.countries.get(x[0]).name] for x in s ]
        return s
    user_scores = get_sorted(user_scores)
    global_scores = get_sorted(global_scores)
    scores_data = json.dumps({
        'user': user_scores, 
        'global': global_scores
        })
    # last_year='2007'
    return render_response('result.html', dict(
        scores_data=scores_data,
        user_scores=user_scores,
        global_scores=global_scores
        ))


## -------------------------
## API

@app.route('/api/indicators')
def questions():
    questions = model.get_questions(g.user_id)
    return jsonify(app, questions)

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    db = get_db()
    if request.method == 'POST': 
        if not (request.form and 'label' in request.form):
            abort(400)
        db.user.update({'user_id': g.user_id}, 
                       {'$set': {'label': request.form.get('label')}}, upsert=True)
    user = db.user.find_one({'user_id': g.user_id})
    if not user:
        return jsonify(app, {})
    return jsonify(app, user)

@app.route('/api/reset', methods=['GET'])
def reset():
    db = get_db()
    db.weighting.remove({'user_id': g.user_id})
    # could keep this as well 
    #db.user.remove({'user_id': user_id}) 
    #del session['id']
    return jsonify(app, {'status': 'ok'})

def json_ready(obj):
    newobj = dict(obj)
    if '_id' in newobj:
        del newobj['_id']
    return newobj

@app.route('/api/weighting', methods=['GET'])
def weighting_get():
    db = get_db()
    rows = [ json_ready(x) for x in db.weighting.find()]
    return jsonify(app, {
        'count': db.weighting.count(),
        'rows': rows
        })

# /api/weighting?NAME=[0.0...1.0]&NAME2=....
@app.route('/api/weighting', methods=['POST'])
def weighting():
    db = get_db()
    if not request.json or not isinstance(request.json, dict): 
        return jsonify(app, {'status': 'error', 
                             'message': 'No data given'})
    if not len(request.json.get('weightings')):
        return jsonify(app, {'status': 'ok', 'message': 'no data'})
    
    weightings = request.json.get('weightings')
    model.save_weightings(weightings, g.user_id)
    return jsonify(app, {'status': 'ok', 'message': 'saved'})

@app.route('/api/aggregate')
def aggregate_api():
    db = get_db() 
    rows = [ json_ready(x) for x in db.aggregate.find().limit(50) ]
    return jsonify(app, {
        'count': db.aggregate.count(),
        'rows': rows
        })

@app.route('/api/datum')
def datum_api():
    db = get_db() 
    rows = []
    for x in db.datum.find().limit(50):
        del x['indicator'] 
        rows.append(x)
    return jsonify(app, rows)



if __name__ == '__main__':

    app.run()

