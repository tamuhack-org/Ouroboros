from django import test
from ouroboros.hacker import models as hacker_models


class SharedTestCase(test.TestCase):
    def setUp(self):
        self.email1 = "dummy@email.com"
        self.password1 = "dummypwd"
        self.first_name1 = "Kennedy"
        self.last_name1 = "Doe"

        self.hacker1 = hacker_models.Hacker(
            email=self.email1,
            password=self.password1,
            first_name=self.first_name1,
            last_name=self.last_name1,
        )
        self.hacker1.save()

        self.email2 = "dummy2@email.com"
        self.password2 = "bigdummypwd"
        self.first_name2 = "John"
        self.last_name2 = "Doe"

        self.hacker2 = hacker_models.Hacker(
            email=self.email2,
            password=self.password2,
            first_name=self.first_name2,
            last_name=self.last_name2,
        )
        self.hacker2.save()