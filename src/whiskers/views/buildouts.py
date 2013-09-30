import json
import zlib
import logging

from datetime import datetime

from pyramid.response import Response
from pyramid.renderers import get_renderer
from whiskers.jsonwrapper import JsonDataWrapper
from whiskers.models import (
    Buildout,
    Package,
    Host,
    Version,
    Settings,
    DBSession)


class BuildoutsView(object):
    """Buildout views."""

    def __init__(self, request):
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()
        self.request = request

    def __call__(self):
        """Main view for whiskers/buildouts."""

        buildouts = self.get_buildouts_info()

        return {'buildouts': buildouts,
                'project': 'whiskers',
                'main': self.main}

    def get_buildouts_info(self):
        """Return list of dicts containing Buildout info."""

        query = DBSession.query(Buildout).join(Buildout.host).\
            group_by(Buildout.name).order_by(Buildout.datetime).\
            all()

        return query

    def post(self):
        """Add a new buildout to database."""
        try:
            data = self.request.params['data']
            incoming = data.encode('utf-8')
            checksum = zlib.adler32(incoming)
            checksum_buildout = Buildout.get_by_checksum(checksum)
            if checksum_buildout:
                logging.info("Checksum matched")
                logging.info("Updating datetime..")
                checksum_buildout.datetime = datetime.now()
                DBSession.flush()
                raise Exception("No changes with existing data.")
            logging.info("New checksum")
            jsondata = JsonDataWrapper(data)
        except KeyError:
            return Response('No data. Nothing added.')
        except Exception as e:
            return Response(str(e))

        host = Host.get_by_name(jsondata.hostname)

        if not host:
            host = Host.add(jsondata.hostname, jsondata.ipv4)

        self.add_buildout(jsondata, host, checksum)

        return Response('Added buildout information to Whiskers.')

    def add_buildout(self, data, host, checksum):
        packages = []

        for package_info in data.packages:
            package = Package.get_by_nameversion(package_info['name'],
                                                 package_info['version'])
            if not package:
                equation = package_info.get('equation', None)
                version = Version.get_by_version(package_info['version']) or\
                    Version.add(package_info['version'], equation)
                requirements = self.get_requirements(
                    package_info['requirements'], data.versionmap)
                package = Package.add(package_info['name'],
                                      version,
                                      requirements)

            packages.append(package)

        buildout = Buildout(data.name, host, checksum, started=data.started,
                            finished=data.finished, packages=packages,
                            config=data.config)

        DBSession.add(buildout)
        self.remove_old_buildouts(data.name)
        return buildout

    def remove_old_buildouts(self, name):
        """Remove old buildouts."""
        buildouts_to_keep = Settings.get_buildouts_to_keep()
        buildouts = Buildout.get_by_name(name)

        if buildouts.count() > buildouts_to_keep and buildouts_to_keep > 0:
            for buildout in buildouts[buildouts_to_keep:]:
                DBSession.delete(buildout)

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
                version = Version.get_by_version(version) or\
                    Version.add(version, equation)
                package = Package.add(req['name'], version)
            packages.append(package)

        return packages

    def buildout_view(self):
        """Return a buildout specified by buildout_id."""
        buildout_id = self.request.matchdict['buildout_id']
        buildout = DBSession.query(Buildout).filter_by(
            id=int(buildout_id)).one()

        new_buildouts = DBSession.query(Buildout).join(Buildout.host).\
            filter(Buildout.host == buildout.host,
                   Buildout.name == buildout.name,
                   Buildout.id != buildout_id,
                   Buildout.datetime > buildout.datetime).\
            order_by(Buildout.datetime).all()

        older_buildouts = DBSession.query(Buildout).join(Buildout.host).\
            filter(Buildout.host == buildout.host,
                   Buildout.name == buildout.name,
                   Buildout.datetime < buildout.datetime,
                   Buildout.id != buildout_id).\
            order_by(Buildout.datetime).all()

        try:
            config = json.loads(buildout.config)
        except TypeError:
            config = None

        return {'buildout': buildout, 'main': self.main, 'config': config,
                'older_buildouts': older_buildouts,
                'new_buildouts': new_buildouts}
