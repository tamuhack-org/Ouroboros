from shared import test
from django.urls import reverse_lazy
from hacker import models as hacker_models


class DeclineViewTestCase(test.SharedTestCase):
    def test_raises_permission_error_when_not_applied(self):
        self.client.force_login(self.hacker)
        response = self.client.post(reverse_lazy("decline"))
        self.assertEqual(response.status_code, 403)

    def test_redirects_when_not_logged_in(self):
        response = self.client.post(reverse_lazy("decline"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('decline')}"
        )

    def test_sets_cant_make_it(self):
        self.create_active_wave()
        app = hacker_models.Application(**self.application_fields, wave=self.wave1)
        app.full_clean()
        app.save()

        self.client.force_login(self.hacker)
        self.client.post(reverse_lazy("decline"))

        self.hacker.refresh_from_db()
        self.assertTrue(self.hacker.cant_make_it)