from datetime import datetime

from sqlalchemy import (
    Column,
    Text,
    Integer,
    DateTime,
    Unicode,
    ForeignKey,
    Table)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

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
    datetime = Column(DateTime)
    checksum = Column(Integer, unique=True)
    host_id = Column(Integer, ForeignKey('host.id'))
    host = relationship("Host",
                        backref=backref('buildouts',
                                        order_by=datetime.desc()))
    packages = relationship("Package", secondary=buildoutpackage_table,
                            backref=backref('buildouts', order_by=name))
    config = Column(Text)

    def __init__(self, name, host, checksum, packages=None, config=None):
        self.name = name
        self.host = host
        if packages:
            self.packages = packages
        if config:
            self.config = config
        self.datetime = datetime.now()
        self.checksum = checksum

    @classmethod
    def get_by_checksum(klass, checksum):
        query = DBSession.query(klass).\
            filter(klass.checksum == checksum).first()
        return query

    @classmethod
    def by_name(klass):
        query = DBSession.query(klass).order_by(klass.name)
        return query

    @classmethod
    def by_host(klass):
        query = DBSession.query(klass).order_by(klass.host)
        return query


@implementer(interfaces.IHost)
class Host(Base):

    __tablename__ = 'host'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(25), unique=True)

    def __init__(self, name):
        self.name = name

    @classmethod
    def all_by_name(klass):
        query = DBSession.query(klass).order_by(klass.name)
        return query

    @classmethod
    def get_by_name(klass, name):
        host = DBSession.query(klass).\
            join(klass.buildouts).\
            filter(klass.name == name).\
            order_by(klass.name).first()
        return host

    @classmethod
    def get_by_id(klass, id):
        host = DBSession.query(klass).\
            join(klass.buildouts).\
            filter(klass.id == id).\
            order_by(klass.name)
        return host.one()

    @classmethod
    def add(klass, hostname):
        host = klass(hostname)
        DBSession.add(host)
        return host


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
        backref="required_by",
        order_by=name)

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

    @classmethod
    def get_packages_by_name(klass, name):
        """Return package filtered by name."""
        try:
            query = DBSession.query(klass).join(Version).\
                filter(klass.name == name).\
                order_by(Version.version.desc())
            return query
        except NoResultFound:
            return None

    @classmethod
    def by_name(klass):
        """Return packages grouped and ordered by name."""
        query = DBSession.query(klass).group_by(klass.name).\
            order_by(klass.name)
        return query

    @classmethod
    def get_by_nameversion(klass, name, version=None):
        query = DBSession.query(klass).join(klass.version).\
            filter(klass.name == name)
        if version:
            query = query.filter(Version.version == version)
        return query.first()

    @classmethod
    def get_by_id(klass, id):
        package = DBSession.query(klass).filter_by(id)

        if package.count():
            return package.first().id

    @classmethod
    def add(klass, name, version=None, requires=None):
        package = klass(name, version=version, requires=requires)
        DBSession.add(package)
        return package


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

    @classmethod
    def get_by_version(klass, version):
        version = DBSession.query(klass).\
            filter(klass.version == version).first()
        return version

    @classmethod
    def add(klass, version, equation):
        version = klass(version, equation=equation)
        DBSession.add(version)
        return version


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
