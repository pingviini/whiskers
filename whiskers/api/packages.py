from cornice.resource import (
    resource,
    view
)
from whiskers.models import (
    DBSession,
    Package
)


@resource(collection_path="/api/packages",
          path="/api/packages/${package_id}")
class Packages(object):

    def __init__(self, request):
        self.request = request

    def collection_get(self):
        """Return all packages as json."""
        results = DBSession.query(Package).order_by(Package.name).all()
        results = [package.get_as_dict() for package in results]
        return {'packages': results}

    @view(renderer='json')
    def get(self):
        package_id = self.request.matchdict.get('package_id')
        package = Packages.get_by_id(package_id)
        return package.get_as_dict()
