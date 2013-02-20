from whiskers.models import DBSession
from whiskers.models import Version


def get_version(version):
    """Returns version id for package"""

    existing_version = Version.get_by_version(version)

    if existing_version.count():
        return existing_version.first().id
    else:
        new_version_id = add_version(version)
        return new_version_id


def add_version(package, version):
    """Add a new version and return its id"""

    existing_version = DBSession.query(Version).filter_by(version=version)

    if not existing_version.count():
        new_version = Version(version)
        DBSession.merge()
        return new_version.id
