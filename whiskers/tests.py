import unittest
import json
import transaction
from chameleon.zpt.template import PageTemplateFile
from pyramid import testing


test_data = {
    "buildoutname": "test",
    "packages": [
        {"version": "0.6.24", "name": "distribute"},
        {"version": "1.1.2", "name": "nose"},
        {"required_by": ["mr.developer 1.18"], "version": "1.5.2", "name": "zc.buildout"},
        {"version": "1.3.2", "name": "zc.recipe.egg"}
    ]
}


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
    config.add_route('buildout_view', '/buildouts/{buildout_id}/view')
    config.add_route('package_view', '/packages/{package_id}/view')


class PackageModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from whiskers.models import Package
        return Package

    def _makeOne(self, name='package', version='1.0'):
        from whiskers.models import Version
        return self._getTargetClass()(name, Version(version))

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'package')
        self.assertEqual(instance.version.version, '1.0')


class BuildoutModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _makeOneBuildout(self, name='buildout'):
        from whiskers.models import Buildout, Package, Version
        return Buildout(name, packages=[Package('package1', Version('1.0')),
                                        Package('package2', Version('1.1'))])

    def test_constructor(self):
        instance = self._makeOneBuildout()
        self.assertEqual(instance.name, 'buildout')
        self.assertTrue(len(instance.packages) == 2)


class InitializeSqlTests(unittest.TestCase):

    def setUp(self):
        from whiskers.models import DBSession
        DBSession.remove()

    def tearDown(self):
        from whiskers.models import DBSession
        DBSession.remove()

    def _callFUT(self, engine):
        from whiskers.models import initialize_sql
        return initialize_sql(engine)

    def _createDummyContent(self, session):
        from whiskers.models import Buildout, Package, Version
        packages = [Package('package1', Version('1.0')), Package('package2',
                            Version('1.1'))]
        buildout = Buildout('buildout', packages=packages)
        session.add(buildout)
        session.flush()
        transaction.commit()

    def test_it(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        self._callFUT(engine)
        from whiskers.models import DBSession, Buildout
        self._createDummyContent(DBSession)
        buildout = DBSession.query(Buildout).one()
        self.assertEqual(buildout.name, 'buildout')
        packages = [u'package1', u'package2']
        versions = [u'1.0', u'1.1']
        buildout_packages = [i.name for i in buildout.packages]
        buildout_versions = [i.version for i in buildout.packages]
        self.assertEqual(packages.sort(), buildout_packages.sort())
        self.assertEqual(versions.sort(), buildout_versions.sort())


class TestWhiskersView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        testing.tearDown()

    def test_whiskers_view(self):
        from whiskers.views import whiskers_view
        request = testing.DummyRequest()
        info = whiskers_view(request)
        self.assertEqual(info['project'], 'whiskers')
        self.assertEqual(info['main'].__class__, PageTemplateFile)


class TestBuildoutsView(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views import buildouts_view
        return buildouts_view(request)

    def test_it(self):
        from whiskers.models import Buildout, Package, Version
        request = testing.DummyRequest()
        buildout = Buildout('buildout1', [Package('package1',Version('1.0'))])
        self.session.add(buildout)
        _registerRoutes(self.config)
        info = self._callFUT(request)
        self.assertEqual(info['buildouts'][0], buildout)


class AddBuildoutTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views import add_buildout_view
        return add_buildout_view(request)

    def add_buildout(self, test_data=test_data):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.params = {'data': json.dumps(test_data)}
        self._callFUT(request)

    def test_it_nodata(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        info = self._callFUT(request)
        self.assertEqual(info.status, u'200 OK')
        self.assertEqual(info.text, u'No data. Nothing added.')

    def test_it_submitted(self):
        self.add_buildout()
        from whiskers.models import Buildout
        buildout = self.session.query(Buildout).filter_by(name='test').one()
        self.assertEqual(buildout.name, u'test')
        packages = [i.name for i in buildout.packages]
        for p in ['distribute', 'nose', 'zc.buildout', 'zc.recipe.egg']:
            self.assertTrue(p in packages)

    def test_update_data(self):
        from whiskers.models import Buildout
        # First we add default data and check it's there
        self.add_buildout()
        buildout = self.session.query(Buildout).filter_by(name='test').one()
        packages = [(i.name, i.version.version) for i in buildout.packages]
        self.assertTrue((u'distribute', u'0.6.24') in packages)
        # Lets update our data
        test_data['packages'][0]['version'] = '0.6.25'
        self.add_buildout(test_data)
        buildout = self.session.query(Buildout).filter_by(name='test').one()
        packages = [(i.name, i.version.version) for i in buildout.packages]
        self.assertTrue((u'distribute', u'0.6.25') in packages)
