from pyramid.renderers import get_renderer
from whiskers.models import DBSession
from whiskers.models import Version


def version_view(request):
    main = get_renderer('whiskers:views/templates/master.pt').implementation()
    session = DBSession()
    version_id = request.matchdict['version_id']
    version = session.query(Version).filter_by(id=int(version_id)).one()
    return {'version': version, 'main': main}


def get_version(version):
    """Returns version id for package"""

    session = DBSession()
    existing_version = session.query(Version).filter_by(version=version)

    if existing_version.count():
        return existing_version.first().id
    else:
        new_version_id = add_version(version)
        return new_version_id


def add_version(package, version):
    """Adds new version and returns its id"""

    session = DBSession()
    existing_version = session.query(Version).filter_by(version=version)

    if not existing_version.count():
        new_version = Version(version)
        session.merge()
        return new_version.id
