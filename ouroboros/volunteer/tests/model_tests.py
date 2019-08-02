from shared import test
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

# Create your tests here.

class TokenTestCase(test.SharedTestCase):
    def test_token_created_on_user_creation(self):
        new_user_fields = {
            "email": "email@tamu.edu",
            "password": "password",
            "is_active": True,
        }
        new_user = get_user_model()(**new_user_fields)
        new_user.save()
        self.assertTrue(Token.objects.filter(user=new_user).exists())