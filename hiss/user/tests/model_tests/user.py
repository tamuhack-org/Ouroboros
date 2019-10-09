from django.test import TestCase

from user.models import User


class UserTestCase(TestCase):
    def setUp(self):
        self.email = "dummy@email.com"
        self.password = "password"

    def test_email_is_lookup(self):
        User.objects.create_user(self.email, self.password)
        self.assertTrue(User.objects.filter(email=self.email).exists())

    def test_user_is_inactive_by_default(self):
        User.objects.create_user(self.email, self.password)
        self.assertFalse(User.objects.get(email=self.email).is_active)
