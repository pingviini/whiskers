import json
import transaction
from pyramid.response import Response
from whiskers.models import DBSession
from whiskers.models import Buildout, Package, Version
from pyramid.renderers import get_renderer


def whiskers_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    return {'project': 'whiskers', 'main': main}


def add_buildout_view(request):
    try:
        data = json.loads(request.params['data'])
    except KeyError:
        return Response('No data. Nothing added.')

    session = DBSession()
    buildoutname = data['buildoutname']
    packages = data['packages']
    prepared_packages = prepare_packages(session, packages)
    buildout = session.query(Buildout).filter_by(name=buildoutname)

    if not buildout.count():
        buildout = Buildout(name=buildoutname, packages=prepared_packages)
    else:
        buildout = buildout[0]
        buildout.packages = prepared_packages
    session.merge(buildout)
    transaction.commit()
    return Response('OK')


def prepare_packages(session, packages):
    packages_list = list()
    for package in packages:
        existing_version = session.query(Version).filter_by(
                version=package['version'])
        existing_package = None
        if existing_version.count():
            version = existing_version.first()
            existing_package = session.query(Package).filter_by(
                    name=package['name'], version=version)
        else:
            version = Version(package['version'])

        if not (existing_package and existing_package.count()):
            package_item = Package(package['name'], version)
        else:
            package_item = existing_package.first()
        packages_list.append(package_item)
    return packages_list


def buildouts_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    session = DBSession()
    buildouts = session.query(Buildout).order_by(Buildout.name).all()
    return {'buildouts': buildouts, 'project': 'whiskers', 'main': main}


def buildout_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    session = DBSession()
    buildout_id = request.matchdict['buildout_id']
    buildout = session.query(Buildout).filter_by(id=int(buildout_id)).one()
    packages = session.query(Package).join(Package.buildouts).filter(
                    Buildout.id == buildout_id).order_by(Package.name).all()
    return {'buildout': buildout, 'main': main, 'packages': packages}


def package_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    session = DBSession()
    package_name = request.matchdict['package_name']
    package_id = request.matchdict['id']

    results = session.query(Package).filter(
        Package.name == package_name)
    packages = results.all()
    packages = sort_versionnumbers(packages)

    if len(package_id) > 0:
        package = results.filter_by(id=int(package_id[0])).first()
    else:
        package = None
    if results.count() > 1:
        other_versions = True
    else:
        other_versions = False

    return {'packages': packages, 'package': package,
            'package_name': package_name, 'main': main,
            'other_versions': other_versions}


def sort_versionnumbers(packages):
    packages.sort(key=lambda x: [int(y) for y in x.version.version.split('.')])
    return packages


def packages_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    session = DBSession()
    packages = session.query(Package).group_by(Package.name).all()
    return {'packages': packages, 'project': 'whiskers', 'main': main}
