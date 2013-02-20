import transaction
import unittest
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
        self.session = _initTestingDB()

    def _createDummyContent(self):
        from whiskers.models import Package, Version
        version = Version('1.0')
        package = Package('req-package-1', version)
        self.session.add(package)
        self.session.flush()
        transaction.commit()

    def _callFUT(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request).package_view()

    def test_it(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        self._callFUT(engine)
        self._createDummyContent()
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        info = self._callFUT(request)
        import pdb; pdb.set_trace()
