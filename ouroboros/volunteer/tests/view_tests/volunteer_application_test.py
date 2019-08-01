from datetime import timedelta

from django.utils import timezone
from django.urls import reverse

from shared import test
from volunteer.models import Shift, VolunteerApplication

from shared import test

class VolunteerApplicationViewTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.vol_app_fields = {
            "first_name": "Kennedy",
            "last_name": "Doe",
            "phone_number": "+12125552368",
            "grad_year": "Spring 2020",
            "shirt_size": "L",
        }

    def create_shift(self) -> Shift:
        start_datetime = timezone.now()
        end_datetime = start_datetime + timedelta(hours=1)
        return Shift.objects.create(start=start_datetime, end=end_datetime)

    def test_only_available_to_logged_in_users(self):
        response = self.client.get(reverse("volunteer-signup"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('volunteer-signup')}"
        )

    def test_cant_submit_unless_logged_in(self):
        shift = self.create_shift()
        self.vol_app_fields["shifts"] = [shift.pk]
        response = self.client.post(
            reverse("volunteer-signup"), data=self.vol_app_fields
        )
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('volunteer-signup')}"
        )

    def test_successful_submission_creates_volunteer_app(self):
        self.client.force_login(self.hacker)
        shift = self.create_shift()
        self.vol_app_fields["shifts"] = [shift.id]
        response = self.client.post(
            reverse("volunteer-signup"), data=self.vol_app_fields
        )
        self.assertTrue(
            VolunteerApplication.objects.filter(hacker=self.hacker).exists()
        )

    def test_successful_submission_sets_shift(self):
        self.client.force_login(self.hacker)
        shift = self.create_shift()
        self.vol_app_fields["shifts"] = [shift.id]
        response = self.client.post(
            reverse("volunteer-signup"), data=self.vol_app_fields
        )
        vol_app = VolunteerApplication.objects.get(hacker=self.hacker)
        self.assertEqual(list(vol_app.shifts.all()), [shift])
