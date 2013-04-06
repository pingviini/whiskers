import unittest
import transaction

from pyramid import testing


def _initTestingDB():
    from sqlalchemy import create_engine
    from whiskers.models import (
        DBSession,
        Base,
    )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession


def _registerRoutes(config):
    config.add_static_view('static', 'whiskers:static', cache_max_age=3600)
    config.add_route('home', '/', request_method='GET')
    config.add_route('post_buildout', '/',
                     request_method='POST')
    config.add_route('buildouts', '/buildouts', request_method="GET")
    config.add_route('add_buildout', '/buildouts/add',
                     request_method='POST')
    config.add_route('buildout_view', '/buildouts/{buildout_id}')
    config.add_route('packages', '/packages')
    config.add_route('package_view', '/packages/{package_name}*id')
    config.add_route('about', '/about')
    config.add_route('hosts', '/hosts')


class ViewHomeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.main import whiskers_view
        return whiskers_view(request)

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(sorted(['project', 'main']),
                         sorted(list(response.keys())))


class ViewAboutTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.about import about_view
        return about_view(request)

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(sorted(['project', 'main']),
                         sorted(list(response.keys())))


class ViewHostsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.hosts import HostsView
        return HostsView(request)()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(sorted(['main', 'results']),
                         sorted(list(response.keys())))
        self.assertEqual(response['results'], [{'count': 0, 'host': None}])


class ViewHostTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.create_host()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def create_host(self):
        from whiskers.models import Host
        with transaction.manager:
            host = Host('localhost', '127.0.0.1')
            self.session.add(host)

    def _callFUT(self, request):
        from whiskers.views.hosts import HostsView
        return HostsView(request).host_view()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict['host_id'] = 1
        response = self._callFUT(request)
        self.assertEqual(sorted(['host', 'main', 'buildouts']),
                         sorted(list(response.keys())))


class ViewBuildoutsTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.buildouts import BuildoutsView
        return BuildoutsView(request)()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(sorted(['project', 'main', 'buildouts']),
                         sorted(list(response.keys())))
        self.assertEqual(response['buildouts'], [])


class ViewBuildoutTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.create_buildout()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def create_buildout(self):
        from whiskers.models import Buildout, Host
        with transaction.manager:
            host = Host('localhost', '127.0.0.1')
            self.session.add(host)
            buildout = Buildout(name="Example", host=host, checksum=1)
            self.session.add(buildout)

    def _callFUT(self, request):
        from whiskers.views.buildouts import BuildoutsView
        return BuildoutsView(request).buildout_view()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict['buildout_id'] = 1
        response = self._callFUT(request)
        self.assertEqual(sorted(['config', 'main', 'buildout', 'new_buildouts',
                                 'older_buildouts']),
                         sorted(list(response.keys())))
        self.assertEqual(response['config'], None)
        self.assertEqual(response['new_buildouts'], [])
        self.assertEqual(response['older_buildouts'], [])
        self.assertEqual(response['buildout'].name, 'Example')


class ViewPackagesTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request)()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(sorted(['project', 'unused', 'packages', 'main']),
                         sorted(list(response.keys())))
        self.assertEqual(response['unused'], [])
        self.assertEqual(response['packages'], [])


class ViewPackageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.create_buildout()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def create_buildout(self):
        from whiskers.models import Buildout, Host, Package, Version
        with transaction.manager:
            host = Host('localhost', '127.0.0.1')
            self.session.add(host)
            version = Version('1.0')
            package = Package('example.package', version=version)
            buildout = Buildout(name="Example", host=host, checksum=1,
                                packages=[package])
            self.session.add(buildout)

    def _callFUT(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request).package_view()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict['id'] = 1
        request.matchdict['package_name'] = 'example.package'
        response = self._callFUT(request)
        self.assertEqual(sorted(['packages', 'other_versions', 'package_name',
                                 'package', 'main', 'requires']),
                         sorted(list(response.keys())))
        self.assertTrue(len(response['packages']) > 0)
        self.assertFalse(response['other_versions'])
        self.assertEqual(response['package_name'], 'example.package')
        self.assertEqual(response['package'].version.version, '1.0')
        self.assertEqual(response['requires'], None)


class ViewSettingsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.settings import SettingsView
        return SettingsView(request)()

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(sorted(['main', 'buildouts_to_keep']),
                         sorted(list(response.keys())))
        self.assertTrue(response['buildouts_to_keep'], -1)


class TestJSONPost(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from whiskers.views.buildouts import BuildoutsView
        return BuildoutsView(request).post()

    def _call_packages_view(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request)()

    def test_it(self):
        _registerRoutes(self.config)
        with open(__file__.rsplit('/', 1)[0] + '/testdata.json', 'r') as data:
            request = testing.DummyRequest(post=True)
            request.params['data'] = data.read()
            response = self._callFUT(request)
            self.assertEqual(
                "Added buildout information to Whiskers.",
                response.text)
        from whiskers.models import Package
        self.assertEqual(self.session.query(Package).count(), 10)

        request = testing.DummyRequest()
        response = self._call_packages_view(request)
        self.assertEqual(sorted(['project', 'unused', 'packages', 'main']),
                         sorted(list(response.keys())))
        self.assertEqual(response['unused'], [])
        self.assertEqual(len(response['packages']), 10)
