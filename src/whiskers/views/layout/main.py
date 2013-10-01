class MainLayout(object):
    """Main layout for whiskers."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.static_url = "%s/static" % self.home_url
