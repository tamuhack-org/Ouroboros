from django.urls import reverse_lazy

from volunteer.tests.test_case import TokenAuthTestCase


class VerifyAuthenticatedViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()


    def test_get_not_logged_in_401(self):
        self.create_active_wave()
        response = self.client.get(reverse_lazy("volunteer:verify"))
        self.assertEqual(response.status_code, 401)

    def test_get_regular_user_403(self):
        self.create_active_wave()
        regular_user_token = self.get_token(self.email, self.password)
        response = self.client.get(
            reverse_lazy("volunteer:verify"),
            HTTP_AUTHORIZATION=regular_user_token
        )

        self.assertEqual(response.status_code, 403)

    def test_get_succeeds_for_volunteer(self):
        self.create_active_wave()
        volunteer_token = self.get_volunteer_token()

        response = self.client.get(
            reverse_lazy("volunteer:verify"),
            HTTP_AUTHORIZATION=volunteer_token
        )

        self.assertEqual(response.status_code, 200)

    def test_get_succeeds_for_admin(self):
        self.create_active_wave()
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.get(
            reverse_lazy("volunteer:verify"),
            HTTP_AUTHORIZATION=admin_token
        )

        self.assertEqual(response.status_code, 200)


