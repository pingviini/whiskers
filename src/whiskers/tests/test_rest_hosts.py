import json
import unittest
import datetime

from pyramid.paster import get_app
from whiskers.models import DBSession, Host
from webtest import TestApp


class RESTHostsTest(unittest.TestCase):

    def setUp(self):
        app = get_app('testing.ini')
        self.test_app = TestApp(app)

    def add_test_buildout(self):
        with open('./src/whiskers/tests/testdata.json', 'r') as json_data:
            data = json.load(json_data)
            data['finished'] = datetime.datetime.now().isoformat()
            resp = self.test_app.post_json('/api/buildouts', data)
        return resp

    def add_host(self):
        host = Host('test_host_1', '1.1.1.1')
        DBSession.add(host)
        DBSession.flush()

    def common_tests(self, resp):
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.status, '200 OK')

    def test_hosts(self):
        resp = self.test_app.get('/api/hosts')
        self.common_tests(resp)

    def test_host_put(self):
        host_data = {'name': 'test_host_2',
                     'ipv4': '2.2.2.2'}
        resp = self.test_app.post_json('/api/hosts', host_data)
        self.common_tests(resp)
        self.assertEqual(resp.json[u'name'], u'test_host_2')
        self.assertEqual(resp.json[u'ipv4'], u'2.2.2.2')

    def test_host_get(self):
        host_data = {'name': 'test_host_3',
                     'ipv4': '3.3.3.3'}
        self.test_app.post_json('/api/hosts', host_data)
        resp = self.test_app.get('/api/hosts/1')
        self.common_tests(resp)

    def test_host_buildouts(self):
        self.add_test_buildout()
        resp = self.test_app.get('/api/hosts/1/buildouts')
        self.common_tests(resp)

    def test_host_buildouts_get(self):
        self.add_test_buildout()
        resp = self.test_app.get('/api/hosts/1/buildouts/1')
        self.common_tests(resp)

if __name__ == '__main__':
    unittest.main()
