import pprint

from openhdi.app import app
import openhdi.aggregates as aggregates
import openhdi.model as model

db = aggregates.get_db()    
agg = aggregates.Aggregator()
our_user = u'testuser'
our_user2 = u'testuser2'
quiz_id = u'yourtopia'

def setup():
    # app.config['MONGODB_DATABASE'] = 'openhditest'
    db.drop_collection('weighting')
    db.drop_collection('aggregate')
    db.drop_collection('quiz')
    model.setup_quiz()
    w = model.Weighting.new(quiz_id, our_user)
    w2 = model.Weighting.new(quiz_id, our_user2)
    # mess with it
    w2['weights'] = [0] * 12
    w2['weights'][0] = 1.0
    db.weighting.insert(w)
    db.weighting.insert(w2)
    # aggregates.update(db, weighting)
    # aggregates.update_global(db)

def teardown():
    db.drop_collection('weighting')
    db.drop_collection('aggregate')

class TestAggregates:
    agg = aggregates.Aggregator()

    # not yet working
    def test_get_scores_by_user(self):
        agg.compute_user_score(our_user)
        scores = dict(agg.scores(our_user))
        assert len(scores) == 186, len(scores)
        assert round(scores['US'], 4) == 0.0583, scores['US']

        agg.compute_user_score(our_user2)
        agg.compute_average_score()

    def test_get_weightings_by_user(self):
        # weightings = agg.weightings(our_user)
        w = model.Weighting.load(quiz_id, our_user)
        assert len(w['question_sets']) == 4
        weights = w['weights']
        assert len(weights) == 12, len(weights)

        assert round(sum(weights),5) == 1, sum(weights) 

    def test_get_avg_weighting(self):
        avg = agg.compute_average_weighting()
        assert avg['count'] == 2
        w = avg['weights']
        assert w[2] == 0, w
        assert w[0] == 0.5, w
        assert round(sum(w), 5) == 1.0, sum(w)

        avgweights = agg.weights()
        assert avgweights['NYGNPPCAPPPCD'] == 1.0/6, avgweights

    def test_setup_quiz(self):
        # out = db.quiz.find_one({'id': quiz_id})
        out = model.Quiz(quiz_id)
        assert len(out['structure']) == 3, len(out['structure'])
        econ = out['structure'][0]
        assert econ['label'] == 'Economy'
        assert econ['proxy'] == 'NYGNPPCAPPPCD', econ['proxy']
        econ_struct = econ['structure']
        assert len(econ_struct) == 4, pprint.pprint(econ_struct)

        for struct in out['structure']:
            assert len(struct['structure']) == 4

        qs = out['indicator_list']
        assert len(qs)  == 12, qs

        

if __name__ == '__main__':
    setup()
    agg.compute(our_user)


