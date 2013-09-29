from cornice.resource import (
    resource,
    view
)
from whiskers.models import (
    DBSession,
    Host
)


@resource(collection_path="/api/hosts", path="/api/hosts/${host_id}")
class Hosts(object):

    def __init__(self, request):
        self.request = request

    def collection_get(self):
        """Return all hosts as json."""
        results = DBSession.query(Host).order_by(Host.name).all()
        results = [host.get_as_dict() for host in results]
        return {'hosts': results}

    @view(renderer='json')
    def get(self):
        host_id = self.request.matchdict.get('host_id')
        host = Host.get_by_id(host_id)
        return host.get_as_dict()
