from persistent.mapping import PersistentMapping
from persistent import Persistent
from BTrees.IOBTree import IOBTree
from whiskers import interfaces
from zope.interface import implements
import random


class Whiskers(PersistentMapping):
    """
    Application root which contains Buildouts, Packages and
    CISettings.
    """
    __parent__ = __name__ = None
    implements(interfaces.IWhiskers)

    def getInt(self):
        return int(round(random.random()*10000))


class WhiskersContainer(object):

    current_id = -1

    def add_item(self, item):
        newid = self.current_id + 1
        self.current_id = newid
        item.__name__ = newid
        self[newid] = item
        return newid


class Packages(IOBTree, WhiskersContainer):
    """
    Packages is container for Package objects.
    """
    implements(interfaces.IPackages)
    current_id = -1


class Package(Persistent):
    """
    Package has attributes for egg name and version.
    """
    implements(interfaces.IPackage)

    def __init__(self, name, version):
        self.name = name
        self.version = version


class Buildouts(IOBTree, WhiskersContainer):
    """
    Buildouts is a container for Buildout objects.
    """
    implements(interfaces.IBuildouts)
    current_id = -1


class Buildout(Persistent):
    """
    Buildout has attributes for buildoutname.
    """
    implements(interfaces.IBuildout)

    def __init__(self, buildoutname, packages):
        self.buildoutname = buildoutname
        self.package_ids = packages


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Whiskers()
        zodb_root['app_root'] = app_root
        packages = Packages()
        packages.__parent__ = app_root
        packages.__name__ = u'packages'
        app_root[u'packages'] = packages
        buildouts = Buildouts()
        buildouts.__parent__ = app_root
        buildouts.__name__ = u'buildouts'
        app_root[u'buildouts'] = buildouts
        import transaction
        transaction.commit()
    return zodb_root['app_root']
