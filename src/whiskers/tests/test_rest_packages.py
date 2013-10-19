import unittest
import json
import datetime

from pyramid.paster import get_app
from whiskers.models import (
    DBSession,
    Package,
    Buildout)

from webtest import TestApp


class RESTPackagesTest(unittest.TestCase):

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

    def test_packages(self):
        resp = self.test_app.get('/api/packages')
        self.common_tests(resp)

    def add_test_buildout(self):
        """Add new buildout to db.

        Use test data, but modifies 'finished' value so that we get unique
        checksum.
        """
        with open('./src/whiskers/tests/testdata.json', 'r') as json_data:
            data = json.load(json_data)
            data['finished'] = datetime.datetime.now().isoformat()
            resp = self.test_app.post_json('/api/buildouts', data)
        return resp

    def test_packages_post_get(self):
        resp = self.add_test_buildout()
        self.common_tests(resp)
        resp = self.test_app.get('/api/packages/1')
        data = json.loads(resp.body.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()