import pprint

from openhdi.app import app
import openhdi.aggregates as aggregates
import openhdi.model as model

db = aggregates.get_db()    
our_user = u'testuser'
quiz_id = u'yourtopia'

def setup():
    # app.config['MONGODB_DATABASE'] = 'openhditest'
    db.drop_collection('weighting')
    db.drop_collection('quiz')
    model.setup_quiz()
    w = model.Weighting.new(quiz_id, our_user)
    db.weighting.insert(w)
    # aggregates.update(db, weighting)
    # aggregates.update_global(db)

class TestAggregates:
    agg = aggregates.Aggregator()

    # not yet working
    def _test_get_scores_by_user(self):
        user_scores = aggregates.get_scores_by_user(db, our_user)
        assert user_scores == [], user_scores

    def test_get_weightings_by_user(self):
        # weightings = self.agg.weightings(our_user)
        w = model.Weighting.load(quiz_id, our_user)
        assert len(w['question_sets']) == 4
        weights = w['weights']
        assert len(weights) == 11, len(weights)

        assert round(sum(weights),5) == 1, sum(weights) 

    def test_setup_quiz(self):
        # out = db.quiz.find_one({'id': quiz_id})
        out = model.Quiz(quiz_id)
        assert len(out['structure']) == 3, len(out['structure'])
        econ = out['structure'][0]
        assert econ['label'] == 'Economy'
        assert econ['proxy'] == 'NYGNPPCAPPPCD', econ['proxy']
        econ_struct = econ['structure']
        assert len(econ_struct) == 4, pprint.pprint(econ_struct)

        qs = out['indicator_list']
        assert len(qs)  == 11, qs

