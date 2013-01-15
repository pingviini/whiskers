from pyramid.renderers import get_renderer
from whiskers.models import DBSession
from whiskers.models import Version


def versions_view(request):
    main = get_renderer('whiskers:views/templates/master.pt').implementation()
    session = DBSession()
    versions = session.query(Version).order_by(Version.name).all()
    return {'versions': versions, 'main': main}
