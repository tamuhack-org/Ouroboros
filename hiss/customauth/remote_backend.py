from django.contrib.auth.backends import RemoteUserBackend
from user.models import User
from django.conf import settings
from http.cookies import SimpleCookie
import logging, jwt, requests

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
            auth_check_req = requests.get(
                settings.AUTH_CHECK_URL, headers={"Cookie": remote_user}
            )
            if (auth_check_req.status_code) != 200:
                raise Exception("Unauthorized")

            return User.objects.get(email=email)

        except User.DoesNotExist:
            new_user = User.objects.create_user(
                email=email, password="", auth_id=auth_check_req.json()["authId"]
            )
            new_user.save()
            return new_user

        except Exception as e:
            logger.error(e)
            return None

    def clean_username(self, raw_cookies):
        cookies = SimpleCookie()
        cookies.load(raw_cookies)
        if "accessToken" not in cookies:
            raise Exception("Unauthorized")

        return jwt.decode(
            cookies["accessToken"].value, key=settings.AUTH_JWT_SECRET, verify=True
        )
