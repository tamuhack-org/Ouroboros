from django.contrib.auth.middleware import RemoteUserMiddleware


class CustomRemoteAuthMiddleware(RemoteUserMiddleware):
    header = 'HTTP_COOKIE'
