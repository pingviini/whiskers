from beaker.cache import cache_region
from cornice.resource import (
    resource,
    view
)
import zlib
from sqlalchemy.orm.exc import NoResultFound
from whiskers.jsonwrapper import JsonDataWrapper
from whiskers.models import (
    DBSession,
    Buildout,
    Host, Package, Version)


@resource(collection_path="/api/buildouts",
          path="/api/buildouts/{buildout_id}")
class BuildoutsAPI(object):

    def __init__(self, request):
        self.request = request

    @cache_region('default_term')
    def collection_get(self):
        """Return all buildouts as json."""
        results = DBSession.query(Buildout).order_by(Buildout.name).all()
        results = [buildout.get_as_dict() for buildout in results]
        return {'buildouts': results}

    def get_checksum(self, data):
        """Return data checksum."""
        incoming = data.encode('utf-8')
        checksum = zlib.adler32(incoming)
        return checksum

    def collection_post(self):
        """Add new buildout to the DB."""
        data = self.request.body
        checksum = self.get_checksum(data)
        json_data = JsonDataWrapper(data)
        host = self.prepare_host(json_data)
        packages = self.prepare_packages(json_data)


        buildout = Buildout(
            name=json_data.name,
            host=host,
            checksum=checksum,
            started=json_data.started,
            finished=json_data.finished,
            packages=packages,
            config=json_data.config)

        DBSession.add(buildout)
        DBSession.flush()
        return {'buildout_id': buildout.id}

    def prepare_host(self, json_data):
        """Adds new host to DB or returns existing."""
        host = Host.get_by_name(json_data.hostname)
        if not host:
            host = Host.add(json_data.hostname, json_data.ipv4)
        return host

    def prepare_packages(self, json_data):
        """Add new packages to DB. Returns list of packages."""
        packages = []

        for package_info in json_data.packages:
            package = Package.get_by_nameversion(package_info['name'],
                                                 package_info['version'])
            if not package:
                package = self.add_package(package_info, json_data.versionmap)

            packages.append(package)

        return packages

    def add_package(self, package_info, versionmap):
        """Add new package to DB."""
        equation = package_info.get('equation', None)
        version = Version.get_by_version(package_info['version']) or \
            Version.add(package_info['version'], equation)
        requirements = self.get_requirements(package_info['requirements'],
                                             versionmap)

        package = Package.add(package_info['name'],
                              version,
                              requirements)
        return package

    def get_requirements(self, requirements, versionmap):
        """Return list of package requirements."""
        packages = []

        for req in requirements:
            name = req.get('name')
            version = req.get('version')
            # Below version related code is crap
            # TODO: Clean the crap
            if not version:
                try:
                    version = versionmap[name]
                except KeyError:
                    version = 'stdlib'
            else:
                if version != versionmap[name]:
                    version = versionmap[name]
            package = Package.get_by_nameversion(name,
                                                 version)
            if not package:
                equation = req.get('equation', None)
                version = Version.get_by_version(version) or \
                    Version.add(version, equation)
                package = Package.add(req['name'], version)
            packages.append(package)

        return packages

    @view(renderer='json')
    def get(self):
        buildout_id = self.request.matchdict.get('buildout_id')
        buildout = Buildout.get_by_id(buildout_id)
        return buildout.get_as_dict()
