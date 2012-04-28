import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'zope.sqlalchemy',
    'Paste'
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='whiskers',
      version='0.2',
      description='Whiskers stores package and version data from buildouts.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Jukka Ojaniemi',
      author_email='jukka.ojaniemi@gmail.com',
      url='http://github.com/pingviini/whiskers',
      keywords='whiskers buildout pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='whiskers',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = whiskers:main
      """,
      )
