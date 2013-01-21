import transaction
import unittest
import json
import os

from pyramid import testing
from chameleon.zpt.template import PageTemplateFile


path = os.path.dirname(os.path.realpath(__file__))


def _initTestingDB():
    from whiskers.models import DBSession
    from whiskers.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


def _registerRoutes(config):
    config.add_static_view('static', 'whiskers:static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('buildouts', '/buildouts')
    config.add_route('buildouts', '/buildouts')
    config.add_route('add_buildout', '/buildouts/add')
    config.add_route('buildout_view', '/buildouts/{buildout_id}')
    config.add_route('packages', '/packages')
    config.add_route('package_view', '/packages/{package_name}*id')
    config.add_route('about', '/about')
    config.add_route('hosts', '/hosts')
    config.add_route('host', '/hosts/{host_id}')


class WhiskersViewTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        testing.tearDown()

    def test_whiskers_view(self):
        from whiskers.views.main import whiskers_view
        request = testing.DummyRequest()
        info = whiskers_view(request)
        self.assertEqual(info['project'], 'whiskers')
        self.assertEqual(info['main'].__class__, PageTemplateFile)


class BuildoutsViewTest(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.buildout import BuildoutView
        return BuildoutView(request).buildouts_view()

    def _createDummyContent(self):
        from whiskers.models import Buildout, Package, Version, Host
        host = Host('localhost')
        version = Version('1.0')
        package = Package('req-package-1', version)
        packages = [Package('package1', version),
                    Package('package2', Version('2.0'),
                            requires=[package])]
        buildout = Buildout('buildout', host, packages=packages)
        self.session.add(buildout)
        self.session.flush()
        transaction.commit()

    def test_it(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        self._callFUT(engine)
        self._createDummyContent()
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        info = self._callFUT(request)
        buildout = info['buildouts'][0]
        self.assertEqual(buildout.name, 'buildout')
        self.assertEqual(buildout.host.name, 'localhost')
        self.assertEqual(len(buildout.packages), 2)
        self.assertEqual(info['project'], 'whiskers')

    def get_testjson(self):
        """Return testdata."""

        with open(path + '/tests/testdata.json') as testdata:
            return testdata.readlines()


class PackagesViewTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestinDB()
# class AddBuildoutTests(unittest.TestCase):
#     def setUp(self):
#         self.session = _initTestingDB()
#         self.config = testing.setUp()
#
#     def tearDown(self):
#         self.session.remove()
#         testing.tearDown()
#
#     def _callFUT(self, request):
#         from whiskers.views import add_buildout_view
#         return add_buildout_view(request)
#
#     def add_buildout(self, test_data=test_data):
#         _registerRoutes(self.config)
#         request = testing.DummyRequest()
#         request.params = {'data': json.dumps(test_data)}
#         self._callFUT(request)
#
#     def test_it_nodata(self):
#         _registerRoutes(self.config)
#         request = testing.DummyRequest()
#         info = self._callFUT(request)
#         self.assertEqual(info.status, u'200 OK')
#         self.assertEqual(info.text, u'No data. Nothing added.')
#
#     def test_it_submitted(self):
#         self.add_buildout()
#         from whiskers.models import Buildout
#         buildout = self.session.query(Buildout).filter_by(name='test').one()
#         self.assertEqual(buildout.name, u'test')
#         packages = [i.name for i in buildout.packages]
#         for p in ['distribute', 'nose', 'zc.buildout', 'zc.recipe.egg']:
#             self.assertTrue(p in packages)
#
#     def test_update_data(self):
#         from whiskers.models import Buildout
#         # First we add default data and check it's there
#         self.add_buildout()
#         buildout = self.session.query(Buildout).filter_by(name='test').one()
#         packages = [(i.name, i.version.version) for i in buildout.packages]
#         self.assertTrue((u'distribute', u'0.6.24') in packages)
#         # Lets update our data
#         test_data['packages'][0]['version'] = '0.6.25'
#         self.add_buildout(test_data)
#         buildout = self.session.query(Buildout).filter_by(name='test').one()
#         packages = [(i.name, i.version.version) for i in buildout.packages]
#         self.assertTrue((u'distribute', u'0.6.25') in packages)
