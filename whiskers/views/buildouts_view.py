import json
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import get_renderer
from whiskers import interfaces
from whiskers.models import Buildout, Package


@view_config(context=interfaces.IBuildouts,
             renderer='whiskers:templates/buildouts.pt')
def view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    return {'project':'whiskers', 'main': main}


@view_config(name=u'add', context=interfaces.IBuildouts)
def add_buildout_view(request):
    data = json.loads(request.params.keys()[0])
    buildoutname = data['buildoutname']
    packages = data['packages']
    package_ids = add_packages(request, packages)
    buildout = Buildout(buildoutname, package_ids)
    buildout.name = u'Foo'
    buildout.__context__ = request.context
    request.context.add_item(buildout)
    return Response('OK')

def add_packages(request, packages):
    context = request.root[u'packages']
    package_ids = list()
    for item in packages:
        package = Package(item['name'], item['version'])
        if 'required_by' in item.keys():
            package.required_by = item['required_by']
        package.__context__ = context
        package_ids.append(context.add_item(package))
    return package_ids
