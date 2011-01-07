from flask import Flask, request, session, abort
from uuid import uuid4
from datetime import datetime
from flaskext.genshi import Genshi, render_response
from mongo import get_db, jsonify
    
app = Flask(__name__)
app.secret_key = "harry" 
genshi = Genshi(app)

@app.before_request
def make_session():
    if not 'id' in session:
        session['id'] = uuid4()

@app.route('/api/indicators')
def questions():
    db = get_db() 
    indicators = db.indicator.find().limit(100)
    return jsonify(app, indicators)

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
    
    def validate_weight(key, value):
        indicator = db.indicator.find_one({'id': key})
        if not indicator:
            abort(400)
        try: 
            weight = float(value)
            assert weight >=0.0, "Too small"
            assert weight <=100.0, "Too big"
        except Exception, e:
            abort(400)
        return (key, weight)
    
    weighting = dict([validate_weight(k, v) for k,v \
        in request.json.items()])
    if sum(weighting.values()) > 101.0:
        abort(400)
    weighting['_date'] = datetime.now() 
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
    indicators = db.indicator.find().limit(100)
    return render_response('quiz.html', dict(questions=indicators))


if __name__ == '__main__':
    app.run(debug=True)

