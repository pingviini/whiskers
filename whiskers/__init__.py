from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from whiskers.models import initialize_sql
from whiskers.views.buildouts import BuildoutsView
from whiskers.views.hosts import HostsView
from whiskers.views.packages import PackagesView
from whiskers.views.settings import SettingsView


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'whiskers:static', cache_max_age=3600)

    config.add_route('home', '/', request_method='GET')
    config.add_route('post_buildout', '/',
                     request_method='POST')
    config.add_view('whiskers.views.main.whiskers_view',
                    route_name='home',
                    renderer='views/templates/main.pt')

    config.add_route('buildouts', '/buildouts', request_method="GET")
    config.add_view(BuildoutsView, route_name='buildouts',
                    renderer='views/templates/buildouts.pt')

    # BBB
    config.add_route('add_buildout', '/buildouts/add',
                     request_method='POST')
    config.add_view(BuildoutsView, route_name='post_buildout', attr="post")
    # BBB
    config.add_view(BuildoutsView, route_name='add_buildout', attr="post")

    config.add_route('buildout_view', '/buildouts/{buildout_id}')
    config.add_view(BuildoutsView, route_name='buildout_view',
                    renderer='views/templates/buildout.pt',
                    attr="buildout_view")

    config.add_route('packages', '/packages')
    config.add_view(PackagesView, route_name='packages',
                    renderer='views/templates/packages.pt')

    config.add_route('delete_package', '/packages/{package_name}/{id}/delete',
                     request_method='POST')
    config.add_view(PackagesView, route_name='delete_package',
                    attr='delete_package', renderer='json',
                    xhr=True)

    config.add_route('package_view', '/packages/{package_name}/{id}')
    config.add_view(PackagesView, route_name='package_view',
                    attr='package_view', renderer='views/templates/package.pt')
    config.add_route('general_package_view', '/packages/{package_name}')
    config.add_view(PackagesView, route_name='general_package_view',
                    attr='package_view', renderer='views/templates/package.pt')

    config.add_route('about', '/about')
    config.add_view('whiskers.views.about.about_view',
                    route_name='about',
                    renderer='views/templates/about.pt')

    config.add_route('hosts', '/hosts')
    config.add_view(HostsView, route_name='hosts',
                    renderer='views/templates/hosts.pt')

    config.add_route('settings', '/settings', request_method="GET")
    config.add_view(SettingsView, route_name='settings',
                    renderer='views/templates/settings.pt')

    config.add_route('save_settings', '/settings',
                     request_method='POST')
    config.add_view(SettingsView, route_name='save_settings',
                    attr='post')

    config.add_route('host', '/hosts/{host_id}')
    config.add_view(HostsView, route_name='host', attr="host_view",
                    renderer='views/templates/host.pt')

    return config.make_wsgi_app()
