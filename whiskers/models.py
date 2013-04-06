from datetime import datetime

from sqlalchemy import (
    Column,
    Text,
    Integer,
    DateTime,
    Unicode,
    ForeignKey,
    Table
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
)

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
    """
    Buildout contains the model and classmethods for storing
    and querying buildout information.
    """

    __tablename__ = 'buildout'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    datetime = Column(DateTime)
    started = Column(DateTime)
    finished = Column(DateTime)
    checksum = Column(Integer, unique=True)
    host_id = Column(Integer, ForeignKey('host.id'))
    config = Column(Text)

    # Many to many relationship to Host
    host = relationship(
        "Host",
        backref=backref('buildouts', order_by=datetime.desc())
    )
    # Many to many relationship to Package
    packages = relationship(
        "Package",
        secondary=buildoutpackage_table,
        backref=backref('buildouts', order_by=name),
        order_by="Package.name"
    )

    def __init__(self, name, host, checksum, started=None, finished=None,
                 packages=None, config=None):
        self.name = name
        self.host = host
        self.datetime = datetime.now()
        self.checksum = checksum
        if started:
            self.started = started
        if finished:
            self.finished = finished
        if packages:
            self.packages = packages
        if config:
            self.config = config

    @classmethod
    def get_by_checksum(klass, checksum):
        query = DBSession.query(klass).\
            filter(klass.checksum == checksum).first()
        return query

    @classmethod
    def get_by_name(klass, name):
        query = DBSession.query(klass).filter(klass.name == name).\
            order_by(klass.datetime.desc())
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
    ipv4 = Column(Text(15))

    def __init__(self, name, ipv4):
        self.name = name
        self.ipv4 = ipv4

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
            filter(klass.id == id).\
            order_by(klass.name)
        return host.one()

    @classmethod
    def add(klass, hostname, ipv4):
        """Add a new host object to DB."""
        host = klass(hostname, ipv4)
        DBSession.add(host)
        return host


@implementer(interfaces.IPackage)
class Package(Base):
    """
    Package contains information about the specific package (name, version
    requirements).

    Each package is contained zero or many buildouts.
    Each Package contains one version.
    """

    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    version_id = Column(Integer, ForeignKey("version.id"))
    version = relationship("Version", backref="packages")
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
            order_by(klass.name).all()
        return query

    @classmethod
    def get_by_nameversion(klass, name, version=None):
        """Return package filtered by name and version."""
        query = DBSession.query(klass).join(klass.version).\
            filter(klass.name == name)
        if version:
            query = query.filter(Version.version == version)
        return query.first()

    @classmethod
    def get_by_id(klass, id):
        """Return package id."""
        package = DBSession.query(klass).filter_by(id)

        if package.count():
            return package.first().id

    @classmethod
    def add(klass, name, version=None, requires=None):
        """Add a new package to DB."""
        package = klass(name, version=version, requires=requires)
        DBSession.add(package)
        return package


@implementer(interfaces.IVersion)
class Version(Base):
    """
    Version contains information and classmethods for storing and
    querying package versions.

    Each version is contained in zero or many packages.
    """

    __tablename__ = 'version'

    id = Column(Integer, primary_key=True)
    version = Column(Unicode(20), unique=True)
    final_version = Column(Unicode(20), unique=True)
    equation = Column(Unicode(2))

    def __init__(self, version, equation=None, final_version=None):
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


@implementer(interfaces.ISettings)
class Settings(Base):
    """
    """

    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    buildouts_to_keep = Column(Integer, nullable=False)

    def __init__(self, buildouts_to_keep):
        self.buildouts_to_keep = buildouts_to_keep

    @classmethod
    def get_buildouts_to_keep(klass):
        result = DBSession.query(klass).first()
        if not result:
            return -1
        return result.buildouts_to_keep


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
