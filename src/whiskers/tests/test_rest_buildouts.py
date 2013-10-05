import unittest

from pyramid.paster import get_app
from whiskers.models import DBSession, Host, Buildout
from webtest import TestApp


def add_buildout(name='test_buildout', host=1, checksum=None):
    """Add buildout to test DB."""
    buildout = Buildout('test_buildout', host=1, checksum=None)
    DBSession.add(buildout)
    DBSession.flush()


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

    def test_buildout_put(self):
        buildout_data = {'name': 'test_buildout_2',
                         'ipv4': '2.2.2.2'}
        resp = self.test_app.post_json('/api/buildouts', buildout_data)
        self.common_tests(resp)
        self.assertEqual(resp.json[u'name'], u'test_buildout_2')
        self.assertEqual(resp.json[u'ipv4'], u'2.2.2.2')

    def test_buildout_get(self):
        buildout_data = {'name': 'test_buildout_3',
                         'ipv4': '3.3.3.3'}
        self.test_app.post_json('/api/buildouts', buildout_data)
        resp = self.test_app.get('/api/buildouts/1')
        self.common_tests(resp)


if __name__ == '__main__':
    unittest.main()
