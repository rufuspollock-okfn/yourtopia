from flask import Flask, request, session
from uuid import uuid4
from flaskext.genshi import Genshi, render_response

from mongo import get_db, jsonify

app = Flask(__name__)
app.secret_key = "harry" 
genshi = Genshi(app)

@app.before_request
def make_session():
    if not 'id' in session:
        session['id'] = uuid4()

@app.route('/api/questions')
def questions():
    db = get_db() 
    indicators = db.indicator.find().limit(100)
    return jsonify(app, indicators)

# /api/weighting?indicator=NAME&weight=[0.0...1.0]
@app.route('/api/weighting') #, method=['POST'])
def submit():
    db = get_db()
    def set_indicator(key, value):
        indicator = db.indicator.find_one({'name': key})
        if not indicator:
            return jsonify(app, {'status': 'error', 
                                 'message': "No such indicator: %s" % key})
        try: 
            weight = float(value)
            assert weight >=0.0, "Too small"
            assert weight <=1.0, "Too big"
        except Exception, e:
            return jsonify(app, {'status': 'error', 
                                 'message': unicode(e)})
        id = unicode(session.get('id'))
        db.user.update({'user_id': id}, 
                       {'votes': {key: weight},
                        'user_id': id},
                       upsert=True)
    
    for key, value in request.args.items():
        set_indicator(key, value)

    for key, value in request.form.items():
        set_indicator(key, value)

    return jsonify(app, {'status': 'ok', 'message': 'saved'})


@app.route('/')
def home():
    questions = [
        {
            'id': 'noise',
            'title': 'Level of noise in your ideal country?',
        },
        {
            'id': 'education',
            'title': 'Investment in a high standard of education?'
        },
        {
            'id': 'inequality',
            'title': 'Inequality'
        }
    ]
    return render_response('index.html', dict(questions=questions))


if __name__ == '__main__':
    app.run(debug=True)

