import os
import unittest

from paste.deploy.loadwsgi import appconfig
from webtest import TestApp
from pyramid import testing

from whiskers import main

here = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(here, 'test.ini'))


def init_testing_db():
    from whiskers.models import DBSession
    from whiskers.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


class UnitTestBase(unittest.TestCase):

    def setUp(self):
        self.session = init_testing_db()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()


class IntegrationTestBase(unittest.TestCase):

    def setUp(self):
        self.session = init_testing_db()
        self.app = TestApp(main({}, **settings))
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()
