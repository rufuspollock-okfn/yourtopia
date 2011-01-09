import pprint

from openhdi.app import app
import openhdi.aggregates as aggregates
import openhdi.model as model

db = aggregates.get_db()    
our_user = 'testuser'

def setup():
    # app.config['MONGODB_DATABASE'] = 'openhditest'
    db.drop_collection('weighting')
    weighting =  {
    "category" : "meta",
    "items" : [
        [
            "economy",
            40
        ],
        [
            "health",
            10
        ],
        [
            "inequality",
            25
        ],
        [
            "education",
            25
        ]
    ],
    "user_id" : our_user,
    "indicators" : [
        "inequality",
        "health",
        "education",
        "economy"
    ]
}
    db.weighting.insert(weighting)
    model.setup_quiz()
    aggregates.update(db, weighting)
    # aggregates.update_global(db)

class TestAggregates:
    agg = aggregates.Aggregator()

    # not yet working
    def _test_get_scores_by_user(self):
        user_scores = aggregates.get_scores_by_user(db, our_user)
        assert user_scores == [], user_scores

    def test_get_weightings_by_user(self):
        weightings = self.agg.weightings(our_user)
        assert len(weightings) == 4, weightings
        assert u'economy' in weightings.keys(), weightings

    def test_setup_quiz(self):
        # out = db.quiz.find_one({'id': 'yourtopia'})
        out = model.Quiz('yourtopia')
        assert len(out['structure']) == 3, len(out['structure'])
        econ = out['structure'][0]
        assert econ['label'] == 'Economy'
        assert econ['proxy'] == 'NYGDPPCAPPPCD', econ['proxy']
        econ_struct = econ['structure']
        assert len(econ_struct) == 4, pprint.pprint(econ_struct)

