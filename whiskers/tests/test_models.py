import unittest
import os
import transaction

path = os.path.dirname(os.path.realpath(__file__))


# from chameleon.zpt.template import PageTemplateFile
# from pyramid import testing


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
    # config.add_route('buildouts', '/buildouts')
    # config.add_route('buildout_view', '/buildouts/{buildout_id}/view')
    # config.add_route('package_view', '/packages/{package_id}/view')


class HostModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from whiskers.models import Host
        return Host

    def _makeOne(self, name='latitude', ipv4='127.0.0.1'):
        return self._getTargetClass()(name, ipv4)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'latitude')


class VersionModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from whiskers.models import Version
        return Version

    def _makeOne(self, version='1.0'):
        return self._getTargetClass()(version)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.version, '1.0')


class PackageModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from whiskers.models import Package
        return Package

    def _makeOne(self, name='package', version='1.0', requires=None):
        from whiskers.models import Version
        return self._getTargetClass()(name, Version(version), requires)

    def _makeTwo(self, name='package', version='1.0'):
        p1 = self._makeOne()
        p2 = self._makeOne(name='package2', requires=[p1])
        return [p1, p2]

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'package')
        self.assertEqual(instance.version.version, '1.0')

    def test_requires(self):
        instances = self._makeTwo()
        self.assertEqual(instances[0], instances[1].requires[0])


class BuildoutModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from whiskers.models import Buildout
        return Buildout

    def _makeOne(self, name='buildout'):
        from whiskers.models import Host
        host = Host('localhost', '127.0.0.1')
        return self._getTargetClass()(name, host, 1234)

    def _makeOneWithPackages(self, name, packages):
        from whiskers.models import Host
        host = Host('localhost', '127.0.0.1')
        return self._getTargetClass()(name, host, 1234, packages=packages)

    def _makePackage(self, name, version):
        from whiskers.models import Package, Version
        version = Version(version)
        return Package(name, version)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'buildout')
        self.assertEqual(instance.host.name, 'localhost')

    def test_constructor_with_packages(self):
        p1 = self._makePackage('package-1', '1.0')
        p2 = self._makePackage('package-2', '2.0')
        p3 = self._makePackage('package-3', '3.0')
        p4 = self._makePackage('package-4', '4.0')
        p4.requires = [p3]
        instance = self._makeOneWithPackages(name='buildout',
                                             packages=[p1, p2, p4])
        self.assertEqual(instance.name, 'buildout')
        self.assertEqual(len(instance.packages), 3)
        self.assertEqual(instance.packages[0].name, 'package-1')
        self.assertEqual(instance.packages[0].version.version, '1.0')
        self.assertEqual(instance.packages[1].version.version, '2.0')
        self.assertEqual(instance.packages[2].version.version, '4.0')
        self.assertEqual(instance.packages[2].requires[0], p3)


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
        from whiskers.models import Buildout, Package, Version, Host
        host = Host('localhost', '127.0.0.1')
        version = Version('1.0')
        package = Package('req-package-1', version)
        packages = [Package('package1', version),
                    Package('package2', Version('2.0'),
                            requires=[package])]
        buildout = Buildout('buildout', host, 12345, packages=packages)
        session.add(buildout)
        session.flush()
        transaction.commit()

    def test_it(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        self._callFUT(engine)
        from whiskers.models import DBSession, Buildout, Package
        self._createDummyContent(DBSession)

        buildout = DBSession.query(Buildout).one()
        self.assertEqual(buildout.name, 'buildout')
        packages = ['package1', 'package2']
        versions = ['1.0', '2.0']
        buildout_packages = [i.name for i in buildout.packages]
        buildout_versions = [i.version.version for i in buildout.packages]

        self.assertEqual(packages.sort(), buildout_packages.sort())
        self.assertEqual(versions.sort(), buildout_versions.sort())
        p1 = DBSession.query(Package).filter(Package.name == 'package2').one()
        self.assertEqual(p1.requires[0].name, 'req-package-1')
        self.assertEqual(buildout.host.name, 'localhost')


# class TestWhiskersView(unittest.TestCase):
#     def setUp(self):
#         self.config = testing.setUp()
#         _initTestingDB()
#
#     def tearDown(self):
#         testing.tearDown()
#
#     def test_whiskers_view(self):
#         from whiskers.views import whiskers_view
#         request = testing.DummyRequest()
#         info = whiskers_view(request)
#         self.assertEqual(info['project'], 'whiskers')
#         self.assertEqual(info['main'].__class__, PageTemplateFile)
#
#
# class TestBuildoutsView(unittest.TestCase):
#     def setUp(self):
#         self.session = _initTestingDB()
#         self.config = testing.setUp()
#
#     def tearDown(self):
#         self.session.remove()
#         testing.tearDown()
#
#     def _callFUT(self, request):
#         from whiskers.views import buildouts_view
#         return buildouts_view(request)
#
#     def test_it(self):
#         from whiskers.models import Buildout, Package, Version
#         request = testing.DummyRequest()
#         buildout = Buildout('buildout1',
#                             [Package('package1',Version('1.0'))])
#         self.session.add(buildout)
#         _registerRoutes(self.config)
#         info = self._callFUT(request)
#         self.assertEqual(info['buildouts'][0], buildout)
#
    # def get_testjson(self):
    #     """Return testdata."""

    #     with open(path + '/tests/testdata.json') as testdata:
    #         return testdata.readlines()
#
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
#         self.assertEqual(info.status, '200 OK')
#         self.assertEqual(info.text, 'No data. Nothing added.')
#
#     def test_it_submitted(self):
#         self.add_buildout()
#         from whiskers.models import Buildout
#         buildout = self.session.query(Buildout).filter_by(name='test').one()
#         self.assertEqual(buildout.name, 'test')
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
#         self.assertTrue(('distribute', '0.6.24') in packages)
#         # Lets update our data
#         test_data['packages'][0]['version'] = '0.6.25'
#         self.add_buildout(test_data)
#         buildout = self.session.query(Buildout).filter_by(name='test').one()
#         packages = [(i.name, i.version.version) for i in buildout.packages]
#         self.assertTrue(('distribute', '0.6.25') in packages)
