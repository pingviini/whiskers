from zope.interface import Interface


class IWhiskers(Interface):
    """
    Application root which contains Buildouts, Packages and
    CISettings.
    """


class IBuildouts(Interface):
    """
    Buildouts class is container for individual Buildout objects.
    """


class IBuildout(Interface):
    """
    Buildout contains info about packages, their versions and actual buildout
    name.
    """


class IPackages(Interface):
    """
    Packages is container for Package objects.
    """


class IPackage(Interface):
    """
    Package has attributes for egg name and version.
    """


class ICISettings(Interface):
    """
    CISettings contains connection settings for continous integration
    server.
    """
