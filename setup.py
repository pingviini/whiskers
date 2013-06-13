import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'python-dateutil',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
]

setup(name='whiskers',
      version='1.0-alpha.3',
      description='whiskers',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Jukka Ojaniemi',
      author_email='jukka.ojaniemi@gmail.com',
      url='https://github.com/pingviini/whiskers',
      keywords='web wsgi pyramid whiskers buildout',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='whiskers.tests',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = whiskers:main
      [console_scripts]
      initialize_whiskers_db = whiskers.scripts.initializedb:main
      """,
      )
