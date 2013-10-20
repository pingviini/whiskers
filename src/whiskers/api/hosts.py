from cornice.resource import (
    resource,
    view
)
from sqlalchemy.orm.exc import NoResultFound
from whiskers.models import (
    DBSession,
    Host,
    Buildout)


@resource(collection_path="/api/hosts", path="/api/hosts/{host_id}")
class HostsAPI(object):

    def __init__(self, request):
        self.request = request

    def collection_get(self):
        """Return all hosts as json."""
        results = DBSession.query(Host).order_by(Host.name).all()
        results = [host.get_as_dict() for host in results]
        return {'hosts': results}

    @view(renderer='json')
    def collection_post(self):
        """Stores host to database."""
        data = self.request.json_body
        host = Host(**data)
        DBSession.add(host)
        DBSession.flush()
        return host.get_as_dict()

    @view(renderer='json')
    def get(self):
        host_id = self.request.matchdict.get('host_id')
        host = Host.get_by_id(host_id)
        return host.get_as_dict()


@resource(collection_path="/api/hosts/{host_id}/buildouts",
          path="/api/hosts/{host_id}/buildouts/{buildout_id}")
class HostsBuildoutsAPI(object):

    def __init__(self, request):
        self.request = request
        self.host_id = self.request.matchdict.get('host_id', None)
        self.buildout_id = self.request.matchdict.get('buildout_id', None)

    def collection_get(self):
        """Return all hosts as json."""
        try:
            host = Host.get_by_id(self.host_id)
            buildouts = [buildout.get_as_dict() for buildout in host.buildouts]
            return {'buildouts': buildouts}
        except NoResultFound:
            return None

    @view(renderer='json')
    def get(self):
        buildout = Buildout.get_by_id(self.buildout_id)
        return {'buildout': buildout.get_as_dict()}
