import os

from paste.deploy.loadwsgi import appconfig

from .dummydata import test_data
from .base import IntegrationTestBase

here = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(here, 'test.ini'))


class WhiskersPackagesTests(IntegrationTestBase):

    def test_get_root(self):
        res = self.app.get('/')
        self.assertEqual(res.status_int, 200)

    def add_package_data(self):
        res = self.app.post_json('/', dict(data=test_data))
        self.assertEqual(res.status_int, 200)
        self.assertEqual("Added buildout information to Whiskers.",
                         res.body)

    def test_no_packages_view(self):
        res = self.app.get('/packages')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'text/html')

    def test_package_detailed_view(self):
        self.add_package_data()
        res = self.app.get('/packages/1')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'text/html')

