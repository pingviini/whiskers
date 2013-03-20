from pyramid.renderers import get_renderer
from whiskers.models import DBSession
from whiskers.models import Host


class HostView(object):

    def __init__(self, request):
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()
        self.request = request

    def __call__(self):
        host_id = self.request.matchdict['host_id']
        host = DBSession.query(Host).filter_by(id=int(host_id)).one()
        return {'host': host, 'main': self.main}
