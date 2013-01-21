from sqlalchemy import (
    Column,
    Text,
    Integer,
    Unicode,
    ForeignKey,
    Table)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref)

from zope.sqlalchemy import ZopeTransactionExtension
from zope.interface import implementer
from whiskers import interfaces


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


buildoutpackage_table = Table(
    'buildoutpackage_table',
    Base.metadata,
    Column('buildout_id', Integer, ForeignKey('buildout.id')),
    Column('package_id', Integer, ForeignKey('package.id'))
)

# packageversion_table = Table('packageversion_table', Base.metadata,
#     Column('package_id', Integer, ForeignKey('package.id')),
#     Column('version_id', Integer, ForeignKey('version.id'))
# )

packagerequires_table = Table(
    'packagerequires_table',
    Base.metadata,
    Column('package_id', Integer, ForeignKey('package.id')),
    Column('required_package_id', Integer, ForeignKey('package.id'))
)


@implementer(interfaces.IBuildout)
class Buildout(Base):

    __tablename__ = 'buildout'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    host_id = Column(Integer, ForeignKey('host.id'))
    host = relationship("Host", backref=backref('buildouts', order_by=id))
    packages = relationship("Package", secondary=buildoutpackage_table,
                            backref=backref('buildouts', order_by=id))
    config = Column(Text)

    def __init__(self, name, host, packages=None, config=None):
        self.name = name
        self.host = host
        if packages:
            self.packages = packages
        if config:
            self.config = config


@implementer(interfaces.IHost)
class Host(Base):

    __tablename__ = 'host'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(25), unique=True)

    def __init__(self, name):
        self.name = name


@implementer(interfaces.IPackage)
class Package(Base):
    """
    Each package is contained zero or many buildouts.
    Each Package contains one version.
    """

    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("version.id"))
    version = relationship("Version", backref="packages")
    name = Column(Unicode(255))
    requires = relationship(
        "Package",
        secondary=packagerequires_table,
        primaryjoin=id == packagerequires_table.c.package_id,
        secondaryjoin=id == packagerequires_table.c.required_package_id,
        backref="required_by")

    def __init__(self, name, version=None, requires=None):
        self.name = name
        self.version = version
        if requires:
            if type(requires) == list:
                self.requires = requires
            elif type(requires) == Package:
                self.requires.append(requires)
            else:
                # We don't know what requires is so we just ignore it
                pass


@implementer(interfaces.IVersion)
class Version(Base):
    """Each version is contained in zero or many packages"""

    __tablename__ = 'version'

    id = Column(Integer, primary_key=True)
    version = Column(Unicode(20), unique=True)
    equation = Column(Unicode(2))

    def __init__(self, version, equation=None):
        self.version = version
        if equation:
            self.equation = equation


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
