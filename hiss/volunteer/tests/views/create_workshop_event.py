from django.urls import reverse_lazy

from application.models import Application, STATUS_CHECKED_IN
from volunteer.models import WorkshopEvent
from volunteer.tests.test_case import TokenAuthTestCase
from volunteer.views import USER_NOT_CHECKED_IN_MSG


class CreateWorkshopEventViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()
        self.data_dict = {"email": self.email}

    def test_post_fails_for_regular_user(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        regular_user_token = self.get_token(self.email, self.password)

        response = self.client.post(
            reverse_lazy("volunteer:workshops"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=regular_user_token,
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(WorkshopEvent.objects.filter(user=self.user).exists())

    def test_post_succeeds_for_volunteer(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        volunteer_token = self.get_volunteer_token()

        response = self.client.post(
            reverse_lazy("volunteer:workshops"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=volunteer_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkshopEvent.objects.filter(user=self.user).exists())

    def test_post_succeeds_for_admin(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.post(
            reverse_lazy("volunteer:workshops"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkshopEvent.objects.filter(user=self.user).exists())

    def test_post_fails_for_not_checked_in_user(self):
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.post(
            reverse_lazy("volunteer:workshops"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertEqual(response.status_code, 412)
        self.assertJSONEqual(response.content, {"error": USER_NOT_CHECKED_IN_MSG})
        self.assertFalse(WorkshopEvent.objects.filter(user=self.user).exists())
