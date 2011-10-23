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
    config.add_view('whiskers.views.whiskers_view',
                    route_name='home',
                    renderer='templates/whiskers_view.pt')

    config.add_route('buildouts', '/buildouts')
    config.add_view('whiskers.views.buildouts_view',
                    route_name='buildouts',
                    renderer='templates/buildouts.pt')

    config.add_route('add', '/buildouts/add')
    config.add_view('whiskers.views.add_buildout_view',
                    route_name='add')

    config.add_route('buildout_view', '/buildouts/{buildout_id}')
    config.add_view('whiskers.views.buildout_view',
                    route_name='buildout_view',
                    renderer='templates/buildout.pt')

    config.add_route('packages', '/packages')
    config.add_view('whiskers.views.packages_view',
                    route_name='packages',
                    renderer='templates/packages.pt')

    config.add_route('package_view', '/packages/{package_name}*id')
    config.add_view('whiskers.views.package_view',
                    route_name='package_view',
                    renderer='templates/package.pt')
    return config.make_wsgi_app()

