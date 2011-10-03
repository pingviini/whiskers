from pyramid.view import view_config
from whiskers.models import MyModel

@view_config(context=MyModel, renderer='whiskers:templates/mytemplate.pt')
def my_view(request):
    return {'project':'whiskers'}
