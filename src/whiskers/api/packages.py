from beaker.cache import cache_region
from cornice.resource import (
    resource,
    view
)
from sqlalchemy.orm.exc import NoResultFound
from whiskers.models import (
    DBSession,
    Package,
    Buildout)


@resource(collection_path="/api/packages",
          path="/api/packages/{package_id}")
class PackagesAPI(object):

    def __init__(self, request):
        self.request = request

    @cache_region('default_term')
    def collection_get(self):
        """Return all packages as json."""
        results = DBSession.query(Package).order_by(Package.name).all()
        results = [package.get_as_dict() for package in results]
        return {'packages': results}

    @view(renderer='json')
    def get(self):
        package_id = self.request.matchdict.get('package_id')
        package = Package.get_by_id(package_id)
        return package.get_as_dict()


@resource(collection_path="/api/buildouts/{buildout_id}/packages",
          path="/api/buildouts/{buildout_id}/packages/{package_id}")
class BuildoutPackagesAPI(object):

    def __init__(self, request):
        self.request = request
        self.buildout_id = request.matchdict.get('buildout_id', None)
        self.package_id = request.matchdict.get('package_id', None)

    @cache_region('default_term')
    def collection_get(self):
        """Return all packages as json."""
        try:
            buildout = Buildout.get_by_id(self.buildout_id)
            return {'packages': [package.get_as_dict() for package in buildout.packages]}
        except NoResultFound:
            return None

    @view(renderer='json')
    def get(self):
        package_id = self.request.matchdict.get('package_id')
        package = Package.get_by_id(package_id)
        return package.get_as_dict()
