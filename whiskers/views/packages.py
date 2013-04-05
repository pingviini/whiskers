from whiskers.models import Package
from pyramid.renderers import get_renderer


class PackagesView(object):

    def __init__(self, request):
        self.request = request
        self.main = get_renderer(
            'whiskers:views/templates/master.pt').implementation()

    def __call__(self):
        """Main view for packages."""
        packages = Package.by_name()
        unused = [{'id': package.id,
                   'name': package.name} for package in packages if
                  not package.buildouts]
        return {'packages': packages,
                'project': 'whiskers',
                'unused': unused,
                'main': self.main}

    def package_view(self):
        """View for individual package."""
        package_name = self.request.matchdict.get('package_name', None)
        package_id = self.request.matchdict.get('id', None)

        packages = Package.get_packages_by_name(package_name)
        requires = None
        other_versions = False

        if len(package_id) > 0:
            package = packages.filter(Package.id == int(package_id[0])).first()
            if package and package.requires:
                requires = package.requires
        else:
            package = None

        if packages.count() > 1:
            other_versions = True

        return {'packages': packages.all(), 'package': package,
                'package_name': package_name, 'main': self.main,
                'other_versions': other_versions,
                'requires': requires}
