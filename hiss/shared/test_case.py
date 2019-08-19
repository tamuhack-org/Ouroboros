from django.test import TestCase

from user.models import User


class SharedTestCase(TestCase):
    """A shared test case that provides utility functions for testing code easily."""

    def __init__(self):
        self.email = "email@dummy.com"
        self.password = "password"
        self.user = User.objects.create_user(email=self.email, password=self.password, is_active=True)

        self.admin_email = "admin@official.com"
        self.admin_password = "admin_password"
        self.admin = User.objects.create_superuser(self.admin_email, self.admin_password, is_active=True)
