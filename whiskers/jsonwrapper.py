import json


class JsonDataWrapper(object):
    """Wrapper for json-data."""

    def __init__(self, data):
        self.data = json.loads(data)

    @property
    def hostname(self):
        return self.data.get('hostname', None)

    @property
    def name(self):
        return self.data.get('buildoutname', None) or\
            self.path.rsplit('/', 1)[-1]

    @property
    def path(self):
        return self.data.get('directory', None)

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
        return self.data.get('executable', None)

    @property
    def allow_picked_versions(self):
        return self.data.get('allow_picked_versions', None)

    @property
    def newest(self):
        return self.data.get('newest', None)

    @property
    def versionmap(self):
        return self.data.get('versionmap', None)

    @property
    def config(self):
        tmp = self.data.copy()
        tmp.pop('packages')
        tmp.pop('versionmap')
        return json.dumps(tmp)

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
