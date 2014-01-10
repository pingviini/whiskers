from .base import IntegrationTestBase
from .dummydata import test_data


class WhiskersRootTests(IntegrationTestBase):

    def test_get_root(self):
        res = self.app.get('/')
        self.assertEqual(res.status_int, 200)

    def test_post_root(self):
        res = self.app.post_json('/', dict(data=test_data))
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.body.decode(),
                         u"Added buildout information to Whiskers.")

        from whiskers.models import (Package, Host)
        self.assertEqual(self.session.query(Package).count(), 10)
        self.assertEqual(self.session.query(Host).count(), 1)

    def test_post_root_with_no_data(self):
        res = self.app.post_json('/', dict())
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.body.decode(), u'No data. Nothing added.')

    def test_post_root_with_garbled_data(self):
        data = '{][}'
        res = self.app.post_json('/', dict(data=data))
        self.assertEqual(res.status_int, 200)
        self.assertTrue(
            u"Not a valid request. Error was: " in res.body.decode())
