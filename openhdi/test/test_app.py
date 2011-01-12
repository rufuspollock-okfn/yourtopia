from flask import json, url_for

from openhdi.app import app, g, QUIZ, url_for
from openhdi.mongo import get_db
db = get_db()

def setup():
    pass

class TestApp():
    def setup(self):
        self.app = app.test_client()

    def teardown(self):
        db.weighting.drop()

    def test_index(self):
        res =  self.app.get('/')
        assert 'Which country is closest' in res.data, res.data

    def test_quiz(self):
        with app.test_client() as c:
            res =  c.get('/quiz/1')
            assert 'Economy' in res.data, res.data
            assert 'Education' in res.data, res.data
            assert 'Current weighting' in res.data, res.data
            assert 'Step 1' in res.data, res.data
            assert '__dimension__' in res.data, res.data
            print g.user_id
            assert g.user_id in res.data, res.data
            # Economy weight
            assert 'value="33"' in res.data, res.data
            assert 'value="34"' in res.data, res.data

        res =  self.app.get('/quiz/2')
        assert 'Household final consumption' in res.data, res.data

        res =  self.app.get('/quiz/3')
        assert 'Prevalence of undernourishment' in res.data, res.data

        res =  self.app.get('/quiz/4')
        assert 'Mean years of schooling' in res.data, res.data

    def test_quiz_post(self):
        data = dict([
            ('weighting-economy-percent', u'30'),
            ('save', u'Next \xbb'),
            ('weighting-education-percent', u'30'),
            ('weighting-health-percent', u'40'),
            ('dimension', '__dimension__')
            ])
        with app.test_client() as c:
            res = c.post('/quiz', data=data)
            userid = g.user_id
            out = db.weighting.find_one({'user_id': userid, 'quiz_id': QUIZ})
            assert out, out
            assert out['sets_done'] == ['__dimension__'], out
            assert out['question_sets']['__dimension__'][0] == [u'economy', 0.30]

            assert res.status == '302 FOUND', res.status
            assert 'quiz/2' in res.data, res.data
    
    def _test_quiz_multistep(self):
        for stage in range(4):
            res = self.app.get('/quiz')
            print stage
            assert 'Step %s' % (stage+1) in res.data, res.data


class TestApi():
    def setup(self):
        self.app = app.test_client()

    def teardown(self):
        pass

    def test_doc(self):
        res = self.app.get('/api/')
        print res.data
        data = json.loads(res.data)
        assert len(data['doc']) == 5, data

    def test_indicator(self):
        res = self.app.get('/api/indicator')
        data = json.loads(res.data)['rows']
        indicator = data[0]
        assert len(data) == 20, len(data)
        labels = sorted([x['label'] for x in data])
        # assert labels == ['Economy', 'Education', 'Health'], labels

    def test_weighting(self):
        res = self.app.get('/api/weighting')

    def test_quiz(self):
        res = self.app.get('/api/quiz')
        data = json.loads(res.data)['rows']
        assert data[0]['id'] == u'yourtopia', data[0]

    def test_admin(self):
        res = self.app.get('/api/admin/aggregate/compute')
        data = json.loads(res.data)
        assert data['status'] == 'ok', data

