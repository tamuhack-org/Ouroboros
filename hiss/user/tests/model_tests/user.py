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

    def test_null_email_rejection(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(None, self.password)
    
    def test_email_uniqueness(self):
        User.objects.create_user(self.email, self.password)
        with self.assertRaises(Exception):
            User.objects.create_user(self.email, "different_password")

    def test_user_activation(self):
        user = User.objects.create_user(self.email, self.password)
        self.assertFalse(user.is_active)
        
        user.is_active = True
        user.save()
        
        user_reloaded = User.objects.get(email=self.email)
        self.assertTrue(user_reloaded.is_active)
