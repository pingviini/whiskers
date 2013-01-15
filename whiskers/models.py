from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import ForeignKey
from sqlalchemy import Table

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension
from zope.interface import implementer
from whiskers import interfaces


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


buildoutpackage_table = Table('buildoutpackage_table', Base.metadata,
    Column('buildout_id', Integer, ForeignKey('buildout.id')),
    Column('package_id', Integer, ForeignKey('package.id'))
)

# packageversion_table = Table('packageversion_table', Base.metadata,
#     Column('package_id', Integer, ForeignKey('package.id')),
#     Column('version_id', Integer, ForeignKey('version.id'))
# )

packagerequires_table = Table('packagerequires_table', Base.metadata,
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

    def __init__(self, name, path=None, host=None, packages=None):
        self.name = name
        self.host = host
        self.packages = packages


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
    requires = relationship("Package",
            secondary=packagerequires_table,
            primaryjoin=id==packagerequires_table.c.package_id,
            secondaryjoin=id==packagerequires_table.c.required_package_id,
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
    # with transaction.manager:
    #     host = Host('localhost')
    #     host2 = Host('zsplones2.cc.jyu.fi')
    #     DBSession.add(host)
    #     DBSession.add(host2)
    #     package2 = Package(u'package2', Version('1.1', '<'))
    #     package3 = Package(u'package3', Version('1.5', '<'))
    #     package4 = Package(u'package4', Version('1.2', '>='))
    #     DBSession.add(package2)
    #     DBSession.add(package3)
    #     DBSession.add(package4)
    #     package1 = Package('package1', Version('1.0'), [package2,package4])
    #     package5 = Package('package5', Version('1.6'), [package3,package4])
    #     DBSession.add(package1)
    #     DBSession.add(package5)
    #     buildout = Buildout('test', host, [package1])
    #     buildout = Buildout('bout', host2, [package5])
    #     DBSession.add(buildout)
    #     DBSession.flush()
