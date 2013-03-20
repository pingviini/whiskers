import json
import dateutil.parser


class JsonDataWrapper(object):
    """Wrapper for json-data."""

    def __init__(self, data):
        self.data = json.loads(data)
        self.buildout = self.data.get('buildout_config')

    @property
    def hostname(self):
        return self.data.get('hostname', None)

    @property
    def ipv4(self):
        return self.data.get('ipv4', None)

    @property
    def started(self):
        date = self.data.get('started', None)
        parsed = dateutil.parser.parse(date)
        return parsed

    @property
    def finished(self):
        date = self.data.get('finished', None)
        parsed = dateutil.parser.parse(date)
        return parsed

    @property
    def name(self):
        return self.buildout.get('buildoutname', None) or\
            self.path.rsplit('/', 1)[-1]

    @property
    def path(self):
        return self.buildout.get('directory', None)

    @property
    def packages(self):
        for package in self.data['packages'].keys():
            package_dict = {
                'name': package,
                'requirements': self.data['packages'][package]['requirements'],
                'version': self.get_package_version(package)}
            yield package_dict

    @property
    def executable(self):
        return self.buildout.get('executable', None)

    @property
    def allow_picked_versions(self):
        return self.buildout.get('allow_picked_versions', None)

    @property
    def newest(self):
        return self.buildout.get('newest', None)

    @property
    def versionmap(self):
        return self.data.get('versionmap', None)

    @property
    def config(self):
        return json.dumps(self.buildout)

    def get_package_version(self, package):
        """Return package version."""

        if not self.data['packages'][package]['version']:
            try:
                version = self.versionmap[package['name']]
            except KeyError:
                version = 'stdlib'
        else:
            version = self.data['packages'][package]['version']
        return version
