import json
import transaction
from pyramid.response import Response
from whiskers.models import DBSession
from whiskers.models import Buildout, Package
from pyramid.renderers import get_renderer


def whiskers_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    return {'project':'whiskers', 'main': main}


def add_buildout_view(request):
    try:
        data = json.loads(request.params.keys()[0])
    except IndexError:
        return Response('No data. Nothing added.')

    session = DBSession()
    buildoutname = data['buildoutname']
    packages = data['packages']
    prepared_packages = prepare_packages(packages)
    buildout = Buildout(name=buildoutname, packages=prepared_packages)
    session.add(buildout)
    session.flush()
    transaction.commit()
    return Response('OK')


def prepare_packages(packages):
    packages_list = list()
    for package in packages:
        packages_list.append(Package(package['name'], package['version']))
    return packages_list

def buildouts_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    session = DBSession()
    buildouts = session.query(Buildout).all()
    return {'buildouts': buildouts, 'project':'whiskers', 'main': main}

def buildout_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    session = DBSession()
    buildout_id = request.matchdict['buildout_id']
    buildout = session.query(Buildout).filter_by(id=int(buildout_id)).one()
    return {'buildout': buildout, 'project':'whiskers', 'main': main}
