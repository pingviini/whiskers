from sqlalchemy.sql.expression import func
from pyramid.renderers import get_renderer
from whiskers.models import DBSession
from whiskers.models import (
    Host,
    Buildout
)


class HostsView(object):

    def __init__(self, request):
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()
        self.request = request

    def __call__(self):
        """Hosts main view."""
        query = self.get_hosts_info()
        return {'results': query, 'main': self.main}

    def host_view(self):
        host_id = self.request.matchdict['host_id']
        host = Host.get_by_id(int(host_id))
        buildouts = self.get_buildouts(host_id)
        return {'host': host,
                'main': self.main,
                'buildouts': buildouts}

    def get_hosts_info(self):
        """Return list of dicts containing Host info."""

        result_list = []

        results = DBSession.query(Host).\
            join(Buildout, Buildout.host_id == Host.id).all()

        for result in results:
            tmp = {}
            tmp['host'] = result
            tmp['count'] = len(result.buildouts)
            result_list.append(tmp)

        return result_list

    def get_buildouts(self, host_id):
        """Return list of buildouts."""
        results = DBSession.query(Buildout).\
            filter(Buildout.host_id == host_id).\
            group_by(Buildout.name).\
            order_by(Buildout.datetime.desc()).all()
        return results
