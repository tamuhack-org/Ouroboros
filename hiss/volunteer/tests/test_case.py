import json

from django.contrib.auth.models import Group
from django.urls import reverse_lazy

from shared import test_case
from user.models import User


class TokenAuthTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.volunteer_group = Group.objects.create(name="volunteer")
        self.volunteer_email = "volunteer@email.com"
        self.volunteer_password = "password"
        self.volunteer = User.objects.create_user(
            email=self.volunteer_email, password=self.volunteer_password, is_active=True
        )
        self.volunteer.groups.set([self.volunteer_group])
        self.volunteer.save()

    def get_token(self, email, password):
        post_body = {"email": email, "password": password}
        response = self.client.post(reverse_lazy("volunteer:login"), data=post_body)
        response_body = json.loads(response.content)
        self.assertIn("token", response_body)
        return " ".join(["Token", response_body["token"]])

    def get_volunteer_token(self):
        return self.get_token(self.volunteer_email, self.volunteer_password)
