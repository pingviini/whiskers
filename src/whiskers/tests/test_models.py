import unittest
import os
import transaction

from .base import UnitTestBase

path = os.path.dirname(os.path.realpath(__file__))


def _registerRoutes(config):
    config.add_static_view('static', 'whiskers:static', cache_max_age=3600)
    config.add_route('home', '/')


class HostModelTests(UnitTestBase):

    def _getTargetClass(self):
        from whiskers.models import Host
        return Host

    def _makeOne(self, name='latitude', ipv4='127.0.0.1'):
        return self._getTargetClass()(name, ipv4)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'latitude')


class VersionModelTests(UnitTestBase):

    def _getTargetClass(self):
        from whiskers.models import Version
        return Version

    def _makeOne(self, version='1.0'):
        return self._getTargetClass()(version)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.version, '1.0')


class PackageModelTests(UnitTestBase):

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


class BuildoutModelTests(UnitTestBase):

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

