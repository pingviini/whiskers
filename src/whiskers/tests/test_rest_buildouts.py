import unittest
import json

from pyramid.paster import get_app
from whiskers.models import (
    DBSession,
    Host,
    Buildout)

from webtest import TestApp


class RESTBuildoutsTest(unittest.TestCase):

    def setUp(self):
        app = get_app('testing.ini')
        self.test_app = TestApp(app)

    def common_tests(self, resp):
        """
        Common tests for buildouts REST API.

        :param resp:
        """
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.status, '200 OK')

    def test_buildouts(self):
        resp = self.test_app.get('/api/buildouts')
        self.common_tests(resp)

    def add_test_buildout(self):
        with open('./src/whiskers/tests/testdata.json', 'r') as json_data:
            resp = self.test_app.post_json('/api/buildouts', json.load(json_data))
        return resp

    def test_buildout_post_get(self):
        resp = self.add_test_buildout()
        self.common_tests(resp)
        resp = self.test_app.get('/api/buildouts/1')
        self.common_tests(resp)


if __name__ == '__main__':
    unittest.main()
