from cornice import Service
from whiskers.models import (
    Package,
    Buildout,
    Host,
    Version,
    DBSession)


package_info = Service(name='package_info',
                       path='/api/package/{package}/{version}',
                       description="Package info.")


@package_info.get()
def get_package_info(request):
    """Returns the information about package."""
    package = request.matchdict['package']
    version = request.matchdict['version']

    result = DBSession.query(Package).\
        outerjoin(Version, Package.version_id == Version.id).\
        filter(Package.name == package,
               Version.version == version).first()

    buildouts = [buildout.name for buildout in result.buildouts]
    buildouts = tuple(set(buildouts))

    result_dict = {'package': result.name,
                   'version': result.version.version,
                   'buildouts': list(buildouts)}

    if result.required_by:
        result_dict['required_by'] = [
            {'name': package.name,
             'version': package.version.version,
             'id': package.id} for package in result.required_by]

    if result.requires:
        result_dict['requires'] = [
            {'name': package.name,
             'version': package.version.version,
             'id': package.id} for package in result.requires]

    return result_dict


host_info = Service(name='host_info',
                    path='/api/host/{host}',
                    description="Host info.")


@host_info.get()
def get_host_info(request):
    """Return information about the host."""
    host = request.matchdict['host']

    result = DBSession.query(Host).\
        filter(Host.name == host).first()
    result_dict = {'host': result.name}

    buildouts = set([buildout.name for buildout in result.buildouts])
    result_dict['buildouts'] = list(buildouts)
    return result_dict


buildout_info = Service(name='buildout_info',
                        path='/api/buildout/{buildout}',
                        description="Buildout info.")


@buildout_info.get()
def get_buildout_info(request):
    """Return information about the latest buildout."""
    buildout = request.matchdict['buildout']

    result = DBSession.query(Buildout).filter(Buildout.name == buildout).\
        order_by(Buildout.datetime).first()
    result_dict = {'name': result.name,
                   'updated': result.datetime.isoformat(),
                   'id': result.id}

    if result.packages:
        packages = [{'name': package.name,
                     'version': package.version.version,
                     'id': package.id} for package in result.packages]
        result_dict['packages'] = packages

    return result_dict
