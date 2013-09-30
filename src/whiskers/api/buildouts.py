from cornice.resource import (
    resource,
    view
)
from whiskers.models import (
    DBSession,
    Buildout
)


@resource(collection_path="/api/buildouts",
          path="/api/buildouts/{buildout_id}")
class BuildoutsAPI(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_get(self):
        """Return all buildouts as json."""
        results = DBSession.query(Buildout).order_by(Buildout.name).all()
        results = [buildout.get_as_dict() for buildout in results]
        return {'buildouts': results}

    @view(renderer='json')
    def get(self):
        buildout_id = self.request.matchdict.get('buildout_id')
        buildout = Buildout.get_by_id(buildout_id)
        return buildout.get_as_dict()
