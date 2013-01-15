from pyramid.renderers import get_renderer
from whiskers.models import (DBSession,
                             Host)


def host_view(request):
    main = get_renderer('whiskers:views/templates/master.pt').implementation()
    session = DBSession()
    host_id = request.matchdict['host_id']
    host = session.query(Host).filter_by(id=int(host_id)).one()
    return {'host': host, 'main': main}
