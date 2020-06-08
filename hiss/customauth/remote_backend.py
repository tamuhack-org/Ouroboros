from django.contrib.auth.backends import RemoteUserBackend
from user.models import User
from django.conf import settings
from http.cookies import SimpleCookie
import logging, jwt, requests

logger = logging.getLogger(__name__)


class GatekeeperRemoteUserBackend(RemoteUserBackend):
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
            auth_check_req = requests.get(
                settings.AUTH_CHECK_URL,
                headers={"Cookie": remote_user, "Accept": "application/json"},
            )
            if (auth_check_req.status_code) != 200:
                raise Exception("Unauthorized")
            user_creds = auth_check_req.json()

            return User.objects.get(auth_id=user_creds["authId"])

        except User.DoesNotExist:
            new_user = User.objects.create_user(
                email=user_creds["email"], password="", auth_id=user_creds["authId"]
            )
            new_user.save()
            return new_user

        except Exception as e:
            logger.error(e)
            return None
