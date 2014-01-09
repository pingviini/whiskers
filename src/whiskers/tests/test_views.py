import transaction
import unittest

from pyramid import testing
from .base import init_testing_db


class UnitTestBase(unittest.TestCase):

    def setUp(self):
        self.session = init_testing_db()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()


class HomeViewTests(UnitTestBase):

    def call_home_view(self, request):
        from whiskers.views.main import whiskers_view
        return whiskers_view(request)

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('home', '/', request_method='GET')

    def test_home_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_home_view(request)
        self.assertEqual(sorted(['project', 'main']),
                         sorted(list(response.keys())))


class AboutViewTests(UnitTestBase):

    def call_about_view(self, request):
        from whiskers.views.about import about_view
        return about_view(request)

    def test_about_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_about_view(request)
        self.assertEqual(sorted(['project', 'main']),
                         sorted(list(response.keys())))

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('about', '/about', request_method='GET')


class HostsViewTests(UnitTestBase):

    def call_hosts_view(self, request):
        from whiskers.views.hosts import HostsView
        return HostsView(request)()

    def call_host_view(self, request):
        from whiskers.views.hosts import HostsView
        return HostsView(request).host_view()

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('hosts', '/hosts')
        self.config.add_route('host', '/hosts/{host_id}')

    def test_hosts_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_hosts_view(request)
        self.assertEqual(sorted(['main', 'results']),
                         sorted(list(response.keys())))
        self.assertEqual(response['results'], [])

    def test_host_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        request.matchdict['host_id'] = 1
        response = self.call_host_view(request)
        self.assertEqual(sorted(['host', 'main', 'buildouts']),
                         sorted(list(response.keys())))


class BuildoutsViewTests(UnitTestBase):

    def call_buildouts_view(self, request):
        from whiskers.views.buildouts import BuildoutsView
        return BuildoutsView(request)()

    def test_buildouts_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_buildouts_view(request)
        self.assertEqual(sorted(['project', 'main', 'buildouts']),
                         sorted(list(response.keys())))
        self.assertEqual(response['buildouts'], [])

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('buildouts', '/buildouts')


class BuildoutViewTests(UnitTestBase):

    def call_buildout_view(self, request):
        from whiskers.views.buildouts import BuildoutsView
        return BuildoutsView(request).buildout_view()

    def create_test_buildout(self):
        from whiskers.models import Buildout, Host
        with transaction.manager:
            host = Host(u'localhost', '127.0.0.1')
            self.session.add(host)
            buildout = Buildout(name=u"Example", host=host, checksum=1)
            self.session.add(buildout)

    def test_buildout_view(self):
        self.register_routes()
        self.create_test_buildout()
        request = testing.DummyRequest()
        request.matchdict['buildout_id'] = 1
        response = self.call_buildout_view(request)
        self.assertEqual(sorted(['config', 'main', 'buildout', 'new_buildouts',
                                 'older_buildouts']),
                         sorted(list(response.keys())))
        from whiskers.models import Buildout
        self.assertTrue(isinstance(response['buildout'], Buildout))
        self.assertEqual(response['config'], None)
        self.assertEqual(response['new_buildouts'], [])
        self.assertEqual(response['older_buildouts'], [])
        self.assertEqual(response['buildout'].name, 'Example')

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('buildout_view', '/buildouts/{buildout_id}')


class PackagesViewTests(UnitTestBase):

    def call_packages_view(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request)()

    def test_packages_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_packages_view(request)
        self.assertEqual(sorted(['project', 'unused', 'packages', 'main']),
                         sorted(list(response.keys())))
        self.assertEqual(response['unused'], [])
        self.assertEqual(response['packages'], [])

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('packages_view', '/packages')


class PackageViewTests(UnitTestBase):

    def create_buildout(self):
        from whiskers.models import (
            Buildout,
            Host,
            Package,
            Version,
        )

        host = Host(u'localhost', '127.0.0.1')
        self.session.add(host)
        version = Version('1.0')
        package = Package(u'example.package', version=version)
        buildout = Buildout(name=u"Example", host=host, checksum=1,
                            packages=[package])
        self.session.add(buildout)

    def call_package_view(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request).package_view()

    def test_package_view(self):
        self.register_routes()
        self.create_buildout()
        request = testing.DummyRequest()
        request.matchdict['id'] = 1
        request.matchdict['package_name'] = 'example.package'
        response = self.call_package_view(request)
        self.assertTrue(len(response['packages']) == 1)
        self.assertEqual(sorted(['packages', 'other_versions', 'package_name',
                                 'package', 'main', 'requires']),
                         sorted(list(response.keys())))

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('package_view', '/packages/{package_name}/{id}')


class ViewSettingsTests(UnitTestBase):

    def call_settings_view(self, request):
        from whiskers.views.settings import SettingsView
        return SettingsView(request)()

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('settings', '/settings', request_method="GET")

    def test_settings_view(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_settings_view(request)
        self.assertEqual(sorted(['main', 'buildouts_to_keep']),
                         sorted(list(response.keys())))
        self.assertTrue(response['buildouts_to_keep'], -1)


class TestJSONPost(UnitTestBase):

    def call_buildout_post(self, request):
        from whiskers.views.buildouts import BuildoutsView
        return BuildoutsView(request).post()

    def call_packages_view(self, request):
        from whiskers.views.packages import PackagesView
        return PackagesView(request)()

    def test_json_post(self):
        self.register_routes()
        request = testing.DummyRequest()
        response = self.call_buildout_post(request)
        self.assertEqual(response.status_int, 200)

    def register_routes(self):
        self.config.include('pyramid_chameleon')
        self.config.add_route('buildouts_view', '/buildouts')
        self.config.add_route('packages_view', '/packages')
        self.config.add_route('buildout_view', '/buildouts/{buildout_id}')



