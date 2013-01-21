import json
# import transaction

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import get_renderer
from sqlalchemy.orm.exc import NoResultFound
from whiskers.models import DBSession
from whiskers.models import Buildout, Package, Host, Version
from whiskers.views.version import get_version
from whiskers.views.package import get_package


class BuildoutView(object):
    """Buildout views."""

    def __init__(self, request):
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()
        self.request = request
        self.session = DBSession()

    @view_config(route_name='buildouts_view')
    def buildouts_view(self):
        """Main view for whiskers/buildouts."""

        return {'buildouts': self.buildouts,
                'project': 'whiskers',
                'main': self.main}

    @property
    def buildouts(self):
        """Return all buildouts"""
        return self.session.query(Buildout).order_by(Buildout.name).all()

    @view_config(route_name='add_buildout')
    def add_buildout_view(self):
        """Add a new buildout to database."""

        try:
            self.jsondata = JsonDataWrapper(self.request.params['data'])
        except KeyError:
            return Response('No data. Nothing added.')

        host = self.get_host(self.jsondata.hostname)

        if host:
            buildout = self.get_existing_buildout(self.jsondata)
            if buildout:
                # self.update(buildout, data)
                pass
            else:
                self.add_buildout(self.jsondata, host)
        else:
            host = self.add_host(self.jsondata.hostname)
            buildout = self.add_buildout(self.jsondata, host)

        return Response('OK. Added buildout')

    def add_package(self, data):
        package = Package(data['name'])

        version = self.get_version(data)
        package.version = version

        if 'requirements' in data:
            requirements = []
            for req in data['requirements']:
                requirements.append(self.get_package(req))
            package.requires = requirements

        self.session.add(package)
        return package

    def get_package(self, package):
        try:
            if not 'version' in package:
                try:
                    version = self.jsondata.versionmap[package['name']]
                except KeyError:
                    version = 'stdlib'
            else:
                version = package['version']

            package = self.session.query(Package).join(Package.version).\
                filter(Package.name == package['name']).\
                filter(Version.version == version).one()
        except NoResultFound:
            package = self.add_package(package)

        return package

    def get_version(self, data):
        try:
            if not 'version' in data:
                try:
                    data['version'] = self.jsondata.versionmap[data['name']]
                except KeyError:
                    # maybe we have standardlib requirement (eg. unittest2)
                    data['version'] = 'stdlib'
            version = self.session.query(Version).filter(
                Version.version == data['version']).one()
        except NoResultFound:
            version = self.add_version(data)

        return version

    def add_version(self, data):
        version = Version(data['version'])
        if 'equation' in data:
            version.equation = data['equation']
        self.session.add(version)

        return version

    def add_host(self, hostname):
        host = Host(hostname)
        self.session.add(host)
        return host

    def add_buildout(self, data, host):
        packages = []

        for package in data.packages:
            packages.append(self.get_package(package))

        buildout = Buildout(data.name, data.path, host, packages,
                            data.config)
        self.session.add(buildout)
        return buildout

    def get_host(self, hostname):
        """Return host object if found."""
        try:
            host = self.session.query(Host).filter(Host.name == hostname).one()
            return host
        except NoResultFound:
            return None

    def get_existing_buildout(self, data):
        """Return buildout if it already exists in db."""
        try:
            buildout = self.session.query(Host).join(Host.buildouts).\
                filter(Host.name == data.hostname).\
                filter(Buildout.name == data.name).one()
            return buildout
        except NoResultFound:
            return None

    # def add(self, data):
    #     """Add buildout to db."""

    #     if packages:
    #         packages_list = []
    #         for package in packages:
    #             requires = []
    #             if package.get('requires'):
    #                 for req in package['requires']:
    #                     pass

    #     buildout = Buildout(name, path, hostname, packages)
    #     return buildout

    @view_config(route_name='buildout_view',
                 renderer='templates/buildout.pt')
    def get(self):
        """Return a buildout specified by buildout_id."""
        buildout_id = self.request.matchdict['buildout_id']
        buildout = self.session.query(Buildout).filter_by(
            id=int(buildout_id)).one()
        packages = self.session.query(Package).join(Package.buildouts).filter(
            Buildout.id == buildout_id).order_by(Package.name).all()
        config = json.loads(buildout.config)

        return {'buildout': buildout, 'main': self.main, 'config': config}

    def update(self, buildout_id):
        """Update existing buildout."""
        # Update buildout path information
        # path = data.get('buildoutpath', None)
        # if path:
        #     buildout.path = path

        # # Update hostname information
        # hostname = data.get('hostname', None)
        # if hostname:
        #     buildout.hostname = hostname

        # # Update packages used by buildout
        # packages = data.get('packages', None)
        # if packages:
        #     buildout.packages = update_buildout_packages(buildout, packages)
        pass

    def delete(self, buildout_id):
        """Delete existing buildout."""
        pass

    def get_buildouts(self):
        """Return all buildouts from database."""
        pass


def update_existing_buildout(buildout, data):
    """Updates buildout information"""

    # Update buildout path information
    path = data.get('buildoutpath', None)
    if path:
        buildout.path = path

    # Update hostname information
    hostname = data.get('hostname', None)
    if hostname:
        buildout.hostname = hostname

    # Update packages used by buildout
    packages = data.get('packages', None)
    if packages:
        buildout.packages = update_buildout_packages(buildout, packages)


def update_buildout_packages(buildout, packages):
    """Update buildout packages"""

    packages_list = []

    for package in packages:
        version_id = get_version(package['version'])
        package_id = get_package(package['name'], version_id)
        packages_list.append(package_id)

    return packages_list


class JsonDataWrapper(object):
    """Wrapper for json-data."""

    def __init__(self, data):
        self.data = json.loads(data)

    @property
    def hostname(self):
        return self.data.get('hostname', None)

    @property
    def name(self):
        return self.data.get('buildoutname', None) or\
            self.path.rsplit('/', 1)[-1]

    @property
    def path(self):
        return self.data.get('directory', None)

    @property
    def packages(self):
        for package in self.data['packages'].keys():
            yield {'name': package,
                   'version': self.data['packages'][package]['version'],
                   'requirements':
                   self.data['packages'][package]['requirements']}

    @property
    def executable(self):
        return self.data.get('executable', None)

    @property
    def allow_picked_versions(self):
        return self.data.get('allow_picked_versions', None)

    @property
    def newest(self):
        return self.data.get('newest', None)

    @property
    def versionmap(self):
        return self.data.get('versionmap', None)

    @property
    def config(self):
        tmp = self.data.copy()
        tmp.pop('packages')
        tmp.pop('versionmap')
        return json.dumps(tmp)
