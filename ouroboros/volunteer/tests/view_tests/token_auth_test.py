import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone

from hacker import models as hacker_models
from shared import test


class TokenAuthTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.volunteer_email = "volunteer@email.com"
        self.volunteer_password = "volunteering_is_good"
        self.volunteer = hacker_models.Hacker(
            email=self.volunteer_email, is_active=True
        )
        self.volunteer.set_password(self.volunteer_password)
        self.volunteer.save()

        self.volunteer_group = Group(name=settings.VOLUNTEER_GROUP_NAME)
        self.volunteer_group.save()
        self.volunteer.groups.add(self.volunteer_group)

    def get_token(self, email, password):
        post_body = {"email": email, "password": password}
        response = self.client.post(reverse("volunteer-login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("token", response_body)
        return " ".join(["Token", response_body["token"]])

    def get_volunteer_token(self):
        return self.get_token(self.volunteer_email, self.volunteer_password)

    def check_in(self, hacker: hacker_models.Hacker):
        hacker.checked_in = True
        hacker.checked_in_datetime = timezone.now()
        hacker.save()
