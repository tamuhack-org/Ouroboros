from rest_framework.authtoken.models import Token

from shared import test_case
from user.models import User


class UserModelReceiverTestCase(test_case.SharedTestCase):
    def test_token_created_when_user_created(self):
        new_user = User.objects.create_user("beep@bop.com", "beepbop")

        self.assertTrue(Token.objects.filter(user=new_user).exists())

    def test_token_created_only_when_user_created(self):
        new_user = User.objects.create_user("beep@bop.com", "beepbop")

        new_user.email = "bop@beep.com"
        new_user.save()

        self.assertEqual(len(Token.objects.filter(user=new_user)), 1)
