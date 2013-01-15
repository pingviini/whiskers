from whiskers.models import DBSession
from whiskers.models import Package
from pyramid.renderers import get_renderer
from pkg_resources import parse_version


def package_view(request):
    main = get_renderer('whiskers:views/templates/master.pt').implementation()
    package_name = request.matchdict['package_name']
    package_id = request.matchdict['id']

    results = DBSession.query(Package).filter(
        Package.name == package_name)
    packages = results.all()
    packages = sort_versionnumbers(packages)
    requires = None

    if len(package_id) > 0:
        package = results.filter_by(id=int(package_id[0])).first()
        requires = package.requires
    else:
        package = None
    if results.count() > 1:
        other_versions = True
    else:
        other_versions = False

    return {'packages': packages, 'package': package,
            'package_name': package_name, 'main': main,
            'other_versions': other_versions,
            'requires': requires}


def sort_versionnumbers(packages):
    try:
        packages.sort(key=lambda x: [
            parse_version(x.version.version)])
    except AttributeError:
        pass
    return packages


def get_package(name, version):
    """Returns package id"""

    package = DBSession.query(Package).filter_by(name).\
            filter_by(version=version)

    if package.count():
        return package.first().id
    else:
        new_package_id = add_package(name, version)
        return new_package_id


def add_package(name, version):
    """Adds new package and returns its id"""

    package = Package(name, version)
    return package.id
