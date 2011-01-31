"""The Flask App
"""
import os
from uuid import uuid4
from datetime import datetime

from flask import Flask, request, session, abort, redirect, g, url_for, flash
from flaskext.genshi import Genshi, render_response
from flask import json
from werkzeug.contrib.fixers import ProxyFix

from openhdi.mongo import get_db
import openhdi.model as model
import openhdi.aggregates as aggregates
from openhdi.api import api


app = Flask(__name__)
# fix for REMOTE_ADDR and HTTP_HOST on reverse proxies
# However causes problems with testing when running on localhost!
# app.wsgi_app = ProxyFix(app.wsgi_app)

def configure_app():
    app.config.from_object('openhdi.settings_default')
    here = os.path.dirname(os.path.abspath( __file__ ))
    # parent directory
    config_path = os.path.join(os.path.dirname(here), 'openhdi.cfg')
    if 'OPENHDI_CONFIG' in os.environ:
        app.config.from_envvar('OPENHDI_CONFIG')
    elif os.path.exists(config_path):
        app.config.from_pyfile(config_path)
    ADMINS = ['rufus.pollock@okfn.org']
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@yourtopia.net',
                                   ADMINS, 'yourtopia.net error')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
configure_app()

genshi = Genshi(app)
QUIZ = app.config['QUIZ']

app.register_module(api, url_prefix='/api')


@app.before_request
def make_session():
    g.db = get_db()
    if not 'id' in session:
        session['id'] = str(uuid4())
    g.user_id = session.get('id') 

# generic stuff
@app.errorhandler(404)
def page_not_found(e):
    values = dict(error='404 - Not Found',
        message='Sorry, what you are looking for is not here'
        )
    return render_response('error.html', values)

@app.errorhandler(500)
def apperror(e):
    values = dict(error='500 - Error',
        message='Sorry, there was an error. We will be looking into it!'
        )
    return render_response('error.html', values)


## ======================
## Routes and Controllers

@app.route('/')
def home():
    total_so_far = g.db.weighting.count()
    return render_response('index.html', dict(
        total_so_far=total_so_far
        ))

@app.route('/quiz')
def quiz():
    # step = int(request.args.get('stage', '1'))
    quiz = model.Quiz(QUIZ)
    
    w = model.Weighting.load(QUIZ, g.user_id, create=True)
    step = len(w['sets_done']) + 1
    if step <= 4:
        return redirect(url_for('quiz_question', step=step))
    if request.args.get('compute', False):
        agg = aggregates.Aggregator()
        agg.compute(g.user_id)
        complete = 1
        return redirect(url_for('result_user', user_id=g.user_id))

    return render_response('quiz.html', dict(
        num_steps=4
        ))


@app.route('/quiz/<int:step>')
def quiz_question(step):
    db = get_db()
    quiz = model.Quiz(QUIZ)

    query = {'id': g.user_id}
    user = db.user.find_one(query)
    if user is None:
        _user = {
            'id': g.user_id,
            'ipaddr': request.remote_addr,
            'created': datetime.now().isoformat()
            }
        db.user.insert(_user)

    w = model.Weighting.load(QUIZ, g.user_id, create=True)
    if step == 1:
        dimension = '__dimension__'
        questions = quiz['structure']
    elif step > 4: # should not be here ..
        return redirect(url_for('quiz'))
    else:
        # use order of dimensions in quiz
        dimension = quiz['structure'][step-2]['id']
        questions = quiz['structure'][step-2]['structure']
    total = 0
    for idx,qu in enumerate(questions):
        _weight = w['question_sets'][dimension][idx][1]
        # percentages
        _weight = int(100*_weight)
        total += _weight
        qu['weight'] = _weight
    # make sure we sum to 100
    # add to random question?
    if total < 100:
        questions[0]['weight'] = questions[0]['weight'] + (100-total)
    return render_response('quiz_question.html', dict(
        questions=questions,
        step=step,
        dimension=dimension,
        ))

@app.route('/quiz', methods=['POST'])
def quiz_submit():
    db = get_db()
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
    if dimension not in w['sets_done']:
        w['sets_done'].append(dimension)
    w.compute_weights()
    w.save()
    # flash('Saved your weightings')
    # return redirect('quiz')
    return quiz()

@app.route('/about')
def about():
    return render_response('about.html')

@app.route('/how')
def how():
    return render_response('how.html')

@app.route('/result')
def result(user_id=None):
    import iso3166
    from openhdi.hdi_gni import data as hdi_gni_data
    def get_sorted(score_set):
        if not score_set:
            return []
        s = score_set
        s = sorted(s, cmp=lambda x,y: -cmp(x[1], y[1]))
        # normalize too (avoid divide by 0)
        ourmax = max(0.00000000001, s[0][1])
        result = []
        for x in s:
            iso_country = iso3166.countries.get(x[0])
            hdi_gni = hdi_gni_data.get(iso_country.alpha3, {"HDI": None, "GNI": None})
            result.append((x[0], round(x[1]/ourmax, 3), iso_country.name, hdi_gni["HDI"], hdi_gni["GNI"]))
        return result
    agg = aggregates.Aggregator()
    global_scores = agg.scores()
    global_scores = get_sorted(global_scores)
    if user_id:
        user_scores = agg.scores(g.user_id)
        user_scores = get_sorted(user_scores)
        weights = agg.weights(g.user_id)
    else:
        weights = agg.weights()
        user_scores = []
    quiz = model.Quiz('yourtopia')
    treeweights = {}
    for dim in quiz['structure']:
        subtree = {}
        for ind in dim['structure']:
            subtree[ind['label']] = weights[ind['id']]
        treeweights[dim['id']] = subtree
    # last_year='2007'
    return render_response('result.html', dict(
        user_scores=user_scores,
        global_scores=global_scores,
        user_scores_json=json.dumps(user_scores),
        global_scores_json=json.dumps(global_scores),
        weights=json.dumps(treeweights)
        ))

# DEPRECATED. Here for backwards compatibility
@app.route('/result/me')
def result_me():
    return result(g.user_id)

@app.route('/result/<user_id>')
def result_user(user_id):
    db = get_db()
    if not db.weighting.find_one({'user_id': user_id}):
        abort(404)
    return result(user_id)

if __name__ == '__main__':
    app.run()

