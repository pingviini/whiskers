import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_whiskers_view(self):
        from whiskers.views.whiskers_view import view
        request = testing.DummyRequest()
        info = view(request)
        self.assertEqual(info['project'], 'whiskers')

    def test_buildouts_view(self):
        from whiskers.views.buildouts_view import view
        request = testing.DummyRequest()
        info = view(request)
        self.assertEqual(info['project'], 'whiskers')

    def test_packages_view(self):
        from whiskers.views.packages_view import view
        request = testing.DummyRequest()
        info = view(request)
        self.assertEqual(info['project'], 'whiskers')
