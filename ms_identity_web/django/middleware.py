try:    
    from ms_identity_web.errors import NotAuthenticatedError
    from django.conf import settings
    from django.shortcuts import render
except:
    pass

from .adapter import DjangoContextAdapter

ms_identity_web = settings.MS_IDENTITY_WEB

class MsalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.ms_identity_web = ms_identity_web
    
    def process_exception(self, request, exception):
        if isinstance(exception, NotAuthenticatedError):
            if hasattr(settings, 'ERROR_TEMPLATE'):
                return render(request, settings.ERROR_TEMPLATE.format(exception.code))                
        return None

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        django_context_adapter = DjangoContextAdapter(request)
        self.ms_identity_web.set_adapter(django_context_adapter)
        django_context_adapter._on_request_init()
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        django_context_adapter._on_request_end()

        return response