from django.contrib.auth.backends import RemoteUserBackend
from user.models import User
from django.conf import settings
from http.cookies import SimpleCookie
import logging
import jwt

logger = logging.getLogger(__name__)


class CustomRemoteBackend(RemoteUserBackend):
    """Set to true in order to create a non-existent user on a successful authentication"""
    create_unknown_user = True

    """Parses cookies and uses the accessToken cookie set by Gatekeeper to
    authenticate a user.

  Keyword arguments:
  request -- Request object
  remote_user -- Contains the request header value specified by CustomRemoteAuthMiddleware
      (Should be the HTTP_COOKIES header)
  """

    def authenticate(self, request, remote_user):
        try:
            user_payload = self.clean_username(remote_user)
            email = user_payload["email"]

            # TODO: Make request to gatekeeper to check validity of user

            user = User.objects.get(email=email)
            return user

        except User.DoesNotExist:
            return User.objects.create_user(email=email, password="")

        except Exception as e:
            logger.error(e)
            return None

    def clean_username(self, raw_cookies):
        cookies = SimpleCookie()
        cookies.load(raw_cookies)
        if "accessToken" not in cookies:
            raise Exception("Unauthorized")

        return jwt.decode(cookies["accessToken"].value, key=settings.AUTH_JWT_SECRET, verify=True)
