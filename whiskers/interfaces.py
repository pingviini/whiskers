from zope.interface import Interface


class IBuildout(Interface):
    """Buildout knows it's packages."""


class IPackage(Interface):
    """Package knows it's name and version."""


class IVersion(Interface):
    """Version"""
