import json

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import get_renderer
from sqlalchemy.orm.exc import NoResultFound
from whiskers.models import DBSession
from whiskers.models import Host


class HostsView(object):
    """Hosts views."""

    def __init__(self, request):
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()
        self.request = request
        self.session = DBSession()

    @view_config(route_name='hosts',
                 renderer='templates/hosts.pt')
    def hosts_view(self):
        """Hosts main view."""
        hosts = self.get_hosts()
        return {'hosts': hosts, 'project': 'whiskers', 'main': self.main}

    def get_host(self, host):
        """Return host"""
        result = DBSession.query(Host).filter_by(name=host)
        if result.count() > 0:
            return result
        else:
            return None

    def get_hosts(self):
        return self.session.query(Host).order_by(Host.name).all()
