from flask import Flask, request
from flaskext.genshi import Genshi, render_response

from mongo import get_db, jsonify

app = Flask(__name__)
genshi = Genshi(app)



@app.route('/api/questions')
def questions():
    db = get_db() 
    indicators = [] 
    for i in db.indicator.find():
        del i['_id']
        indicators.append(i)
    return jsonify(app, indicators)

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

