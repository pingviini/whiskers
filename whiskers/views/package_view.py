from pyramid.view import view_config
from pyramid.renderers import get_renderer
from whiskers import interfaces

@view_config(context=interfaces.IPackage,
             renderer='whiskers:templates/package_view.pt')
def package_view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    return {'project':'whiskers', 'main': main}


