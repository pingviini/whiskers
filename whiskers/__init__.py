from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from whiskers.models import initialize_sql


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'whiskers:static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_view('whiskers.views.main.whiskers_view',
                    route_name='home',
                    renderer='views/templates/main.pt')

    config.add_route('buildouts', '/buildouts')
    config.add_view('whiskers.views.buildouts.buildouts_view',
                    route_name='buildouts',
                    renderer='views/templates/buildouts.pt')

    config.add_route('add_buildout', '/buildouts/add')
    # config.add_view('whiskers.views.buildout.add_buildout_view',
    #                 route_name='add')

    config.add_route('buildout_view', '/buildouts/{buildout_id}')
    # config.add_view('whiskers.views.buildout.buildout_view',
    #                 route_name='buildout_view',
    #                 renderer='views/templates/buildout.pt')

    config.add_route('packages', '/packages')
    config.add_view('whiskers.views.packages.packages_view',
                    route_name='packages',
                    renderer='views/templates/packages.pt')

    config.add_route('package_view', '/packages/{package_name}*id')
    config.add_view('whiskers.views.package.package_view',
                    route_name='package_view',
                    renderer='views/templates/package.pt')

    config.add_route('about', '/about')
    config.add_view('whiskers.views.about.about_view',
                    route_name='about',
                    renderer='views/templates/about.pt')

    config.add_route('hosts', '/hosts')

    config.add_route('host', '/hosts/{host_id}')
    config.add_view('whiskers.views.host.host_view',
                    route_name='host',
                    renderer='views/templates/host.pt')

    config.scan()
    return config.make_wsgi_app()
