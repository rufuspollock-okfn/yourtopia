"""API
"""
from flask import Module, request, session, abort, redirect, g, url_for, flash, Response

from .mongo import get_db, MongoEncoder
import openhdi.aggregates as aggregates

api = Module(__name__)

def jsonify(obj):
    content = MongoEncoder().encode(obj) 
    if 'callback' in request.args:
        content = str(request.args.get('callback')) + '(' + content+ ')'
    return Response(content, mimetype='application/json')


@api.route('/')
def doc():
    items = ['indicator', 'profile', 'admin', 'weighting', 'aggregate']
    out = {
        'doc': []
    }
    for item in sorted(items):
        out['doc'].append({item:  {}})
    return jsonify(out)

@api.route('/indicator')
def indicator():
    db = get_db()
    rows = db.indicator.find().limit(20)
    return jsonify({
        'count': db.indicator.count(),
        'rows': rows
        })

@api.route('/profile', methods=['GET', 'POST'])
def profile():
    db = get_db()
    if request.method == 'POST': 
        if not (request.form and 'label' in request.form):
            abort(400)
        db.user.update({'user_id': g.user_id}, 
                       {'$set': {'label': request.form.get('label')}}, upsert=True)
    user = db.user.find_one({'user_id': g.user_id})
    if not user:
        return jsonify({})
    return jsonify(user)

@api.route('/reset', methods=['GET'])
def reset():
    db = get_db()
    db.weighting.remove({'user_id': g.user_id})
    # could keep this as well 
    #db.user.remove({'user_id': user_id}) 
    #del session['id']
    return jsonify({'status': 'ok'})

@api.route('/weighting', methods=['GET'])
def weighting_get():
    db = get_db()
    rows = db.weighting.find().limit(20)
    return jsonify({
        'count': db.weighting.count(),
        'rows': rows
        })

@api.route('/admin/weighting/delete', methods=['GET'])
def admin_weighting_delete():
    db = get_db()
    db.weighting.drop()
    db.aggregate.drop()
    return jsonify({
        'error': '',
        'status': 'ok'
        })

@api.route('/admin/aggregate/compute', methods=['GET'])
def admin_aggregate_compute():
    agg = aggregates.Aggregator()
    agg.compute_all()
    # return redirect(url_for('aggregate_api'))
    return jsonify({
        'error': '',
        'status': 'ok'
        })

@api.route('/aggregate')
def aggregate():
    db = get_db() 
    rows = db.aggregate.find().limit(20)
    return jsonify({
        'count': db.aggregate.count(),
        'rows': rows
        })

@api.route('/datum')
def datum():
    db = get_db() 
    rows = []
    for x in db.datum.find().limit(50):
        del x['indicator'] 
        rows.append(x)
    return jsonify(rows)

@api.route('/quiz')
def quiz():
    db = get_db() 
    rows = db.quiz.find().limit(50)
    return jsonify({
        'count': db.quiz.count(),
        'rows': rows
        })

