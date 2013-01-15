from whiskers.models import DBSession
from whiskers.models import Package
from pyramid.renderers import get_renderer


def packages_view(request):
    main = get_renderer('whiskers:views/templates/master.pt').implementation()
    packages = get_packages()
    return {'packages': packages, 'project': 'whiskers', 'main': main}


def get_packages():
    """Return packages"""
    session = DBSession()
    return session.query(Package).group_by(Package.name).all()
