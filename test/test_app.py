from flask import json, url_for

from yourtopia.web import app, db

class TestApp():
    def setup(self):
        self.app = app.test_client()

    def teardown(self):
        pass

    def test_index(self):
        res =  self.app.get('/')
        assert 'Yourtopia Italia' in res.data, res.data

