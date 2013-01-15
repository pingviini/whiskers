from whiskers.models import DBSession
from whiskers.models import Buildout
from pyramid.renderers import get_renderer


def buildouts_view(request):
    main = get_renderer('whiskers:views/templates/master.pt').implementation()
    buildouts = get_buildouts()
    return {'buildouts': buildouts, 'project': 'whiskers', 'main': main}


def get_buildouts():
    """Return buildouts"""
    session = DBSession()
    return session.query(Buildout).order_by(Buildout.name).all()
