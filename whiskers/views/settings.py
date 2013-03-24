from pyramid.renderers import get_renderer
from pyramid.httpexceptions import (
    HTTPFound,
)
from whiskers.models import (
    DBSession,
    Settings)


class SettingsView(object):

    def __init__(self, request):
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()
        self.request = request

    def __call__(self):
        """Settings main view."""

        buildouts_to_keep = Settings.get_buildouts_to_keep()
        return {'buildouts_to_keep': buildouts_to_keep, 'main': self.main}

    def post(self):
        """Save settings."""
        try:
            buildouts_to_keep = int(self.request.params['buildouts_to_keep'])
            settings = DBSession.query(Settings).first()
            if not settings:
                settings = Settings(buildouts_to_keep)
            else:
                if buildouts_to_keep != settings.buildouts_to_keep:
                    settings.buildouts_to_keep = buildouts_to_keep
            DBSession.add(settings)
            return HTTPFound(location=self.request.route_url('settings'))
        except:
            pass
