from pyramid.view import view_config
from pyramid.renderers import get_renderer
from whiskers import interfaces

@view_config(context=interfaces.IPackages, renderer='whiskers:templates/packages_view.pt')
def view(request):
    main = get_renderer('whiskers:templates/master.pt').implementation()
    return {'project':'whiskers', 'main': main}

