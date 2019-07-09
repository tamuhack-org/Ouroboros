from shared import test
from rest_framework.authtoken.models import Token
from django.shortcuts import reverse

class ViewTestCase(test.SharedTestCase):
    
    def test_authentication_actually_gets_token(self):
        self.assertTrue(Token.objects.filter(user=self.hacker).exists())
        self.assertTrue(self.hacker.is_active)
        post_body = {
            "username": "",
            "email": self.email,
            "password": self.password
        }
        response = self.client.post(reverse("api-login"), data=post_body)
        print(response.content)