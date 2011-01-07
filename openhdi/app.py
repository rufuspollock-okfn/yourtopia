from flask import Flask, request
from flaskext.genshi import Genshi, render_response

app = Flask(__name__)
genshi = Genshi(app)

@app.route('/api/questions')
def questions():
    from mongo import get_db, jsonify
    db = get_db() 
    indicators = [] 
    for i in db.indicator.find():
        del i['_id']
        indicators.append(i)
    return jsonify(app, indicators)

@app.route('/')
def home():
    return render_response('index.html')

@app.route('/quiz')
def quiz():
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
    return render_response('quiz.html', dict(questions=questions))


if __name__ == '__main__':
    app.run(debug=True)

