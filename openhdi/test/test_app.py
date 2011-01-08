from flask import json, url_for

from openhdi.app import app

def setup():
    pass

class TestApp():
    def setup(self):
        self.app = app.test_client()

    def teardown(self):
        pass

    def test_index(self):
        res =  self.app.get('/')
        assert 'Ever wanted to find out' in res.data, res.data

    def test_quiz(self):
        res =  self.app.get('/quiz')
        assert 'How important are each of the' in res.data, res.data
        assert 'Economy' in res.data, res.data
        assert 'Education' in res.data, res.data
        assert 'Current weighting' in res.data, res.data

class TestApi():
    def setup(self):
        self.app = app.test_client()

    def teardown(self):
        pass

    def test_indicator(self):
        res = self.app.get('/api/indicators')
        data = json.loads(res.data)
        assert len(data) == 4, data
        labels = sorted([x['label'] for x in data ])
        assert labels == ['Economy', 'Education', 'Health', 'Inequality'], labels

    def test_weighting(self):
        res = self.app.post('/api/indicators')
        pass

#    def test_create(self):
#        import re
#        payload = json.dumps({'name': 'Foo'})
#        response = self.app.post('/annotations', data=payload, content_type='application/json')
#
#        # See http://bit.ly/gxJBHo for details of this change.
#        # assert response.status_code == 303, "response should be 303 SEE OTHER"
#        # assert re.match(r"http://localhost/store/\d+", response.headers['Location']), "response should redirect to read_annotation url"
#
#        assert response.status_code == 200, "response should be 200 OK"
#        data = json.loads(response.data)
#        assert 'id' in data, "annotation id should be returned in response"
#
#    def test_read(self):
#        Annotation(text=u"Foo", id=123)
#        session.commit()
#        response = self.app.get('/annotations/123')
#        data = json.loads(response.data)
#        assert data['id'] == 123, "annotation id should be returned in response"
#        assert data['text'] == "Foo", "annotation text should be returned in response"
#
#    def test_read_notfound(self):
#        response = self.app.get('/annotations/123')
#        assert response.status_code == 404, "response should be 404 NOT FOUND"
#
#    def test_update(self):
#        ann = Annotation(text=u"Foo", id=123)
#        session.commit() # commits expire all properties of `ann'
#
#        payload = json.dumps({'id': 123, 'text': 'Bar'})
#        response = self.app.put('/annotations/123', data=payload, content_type='application/json')
#
#        assert ann.text == "Bar", "annotation wasn't updated in db"
#
#        data = json.loads(response.data)
#        assert data['text'] == "Bar", "update annotation should be returned in response"
#
#    def test_update_notfound(self):
#        response = self.app.put('/annotations/123')
#        assert response.status_code == 404, "response should be 404 NOT FOUND"
#
#    def test_delete(self):
#        ann = Annotation(text=u"Bar", id=456)
#        session.commit()
#
#        response = self.app.delete('/annotations/456')
#        assert response.status_code == 204, "response should be 204 NO CONTENT"
#
#        assert Annotation.get(456) == None, "annotation wasn't deleted in db"
#
#    def test_delete_notfound(self):
#        response = self.app.delete('/annotations/123')
#        assert response.status_code == 404, "response should be 404 NOT FOUND"
#
#    def test_search(self):
#        uri1 = u'http://xyz.com'
#        uri2 = u'urn:uuid:xxxxx'
#        user = u'levin'
#        user2 = u'anna'
#        anno = Annotation(
#                uri=uri1,
#                text=uri1,
#                user=user,
#                )
#        anno2 = Annotation(
#                uri=uri1,
#                text=uri1 + uri1,
#                user=user2,
#                )
#        anno3 = Annotation(
#                uri=uri2,
#                text=uri2,
#                user=user
#                )
#        session.commit()
#        annoid = anno.id
#        anno2id = anno2.id
#        session.remove()
#
#        url = '/search'
#        res = self.app.get(url)
#        body = json.loads(res.data)
#        assert body['total'] == 3, body
#
#        url = '/search?limit=1'
#        res = self.app.get(url)
#        body = json.loads(res.data)
#        assert body['total'] == 3, body
#        assert len(body['rows']) == 1
#
#        url = '/search?uri=' + uri1 + '&all_fields=1'
#        res = self.app.get(url)
#        body = json.loads(res.data)
#        assert body['total'] == 2, body
#        out = body['rows']
#        assert len(out) == 2
#        assert out[0]['uri'] == uri1
#        assert out[0]['id'] in [ annoid, anno2id ]
#
#        url = '/search?uri=' + uri1
#        res = self.app.get(url)
#        body = json.loads(res.data)
#        assert body['rows'][0].keys() == ['id'], body['rows']
#
#        url = '/search?limit=-1'
#        res = self.app.get(url)
#        body = json.loads(res.data)
#        assert len(body['rows']) == 3, body
#
#    def test_cors_preflight(self):
#        response = self.app.open('/annotations', method="OPTIONS")
#
#        headers = dict(response.headers)
#
#        assert headers['Access-Control-Allow-Methods'] == 'GET, POST, PUT, DELETE', \
#            "Did not send the right Access-Control-Allow-Methods header."
#
#        assert headers['Access-Control-Allow-Origin'] == '*', \
#            "Did not send the right Access-Control-Allow-Origin header."
#
#        assert headers['Access-Control-Expose-Headers'] == 'Location', \
#                "Did not send the right Access-Control-Expose-Headers header."

