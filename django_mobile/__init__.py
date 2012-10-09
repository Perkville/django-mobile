import threading
from django.core.exceptions import ImproperlyConfigured
from django_mobile.conf import settings


_local = threading.local()


def get_flavour(request=None, default=None):
    request = request or getattr(_local, 'request', None)

    # attempt to get the flavour from the request
    flavour = getattr(request, 'flavour', None)

    # get flavour from session if enabled
    if not flavour and request and settings.FLAVOURS_SESSION_KEY:
        flavour = request.session.get(settings.FLAVOURS_SESSION_KEY, None)

    # if set out of a request-response cycle its stored on the thread local
    if not flavour:
        flavour = getattr(_local, 'flavour', default)

    # if something went wrong we return the very default flavour
    if flavour not in settings.FLAVOURS:
        flavour = settings.FLAVOURS[0]

    return flavour


def set_flavour(flavour, request=None, permanent=False):
    if flavour not in settings.FLAVOURS:
        raise ValueError(
            u"'%r' is no valid flavour. Allowed flavours are: %s" % (
                flavour,
                ', '.join(settings.FLAVOURS),))
    request = request or getattr(_local, 'request', None)
    if request:
        request.flavour = flavour
        if permanent:
            if not settings.FLAVOURS_SESSION_KEY:
                raise ImproperlyConfigured(
                    u"You must specify the FLAVOURS_SESSION_KEY setting to "
                    u"use the 'permanent' parameter.")
            request.session[settings.FLAVOURS_SESSION_KEY] = flavour
    elif permanent:
        raise ValueError(
            u'Cannot set flavour permanently, no request available.')
    _local.flavour = flavour


def _set_request(request):
    _local.request = request
