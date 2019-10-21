from django.urls import reverse_lazy

from application.models import Application
from rsvp.models import Rsvp
from shared import test_case


class UpdateRsvpViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.rsvp_fields = {
            "shirt_size": "XS",
            "dietary_restrictions": ["Vg", "V", "H", "FA", "K"],
            "notes": "",
            "transport_type": "bus-tu",
        }

    def test_get_redirects_when_not_authenticated(self):
        rsvp = Rsvp(**self.rsvp_fields, user=self.user)
        rsvp.save()
        response = self.client.get(reverse_lazy("rsvp:update", args=(rsvp.pk,)))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('rsvp:update', args=(rsvp.pk,))}",
        )

    def test_get_fails_when_not_owner(self):
        rsvp = Rsvp(**self.rsvp_fields, user=self.user)
        rsvp.save()
        self.client.force_login(self.admin)

        response = self.client.get(reverse_lazy("rsvp:update", args=(rsvp.id,)))

        self.assertEqual(response.status_code, 403)

    def test_get_succeeds_when_accessing_owned_rsvp(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        rsvp = Rsvp(**self.rsvp_fields, user=self.user)
        rsvp.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("rsvp:update", args=(rsvp.id,)))

        self.assertEqual(response.status_code, 200)

    def test_post_fails_when_not_owner(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        rsvp = Rsvp(**self.rsvp_fields, user=self.user)
        rsvp.save()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse_lazy("rsvp:update", args=(rsvp.id,)), self.rsvp_fields
        )

        self.assertEqual(response.status_code, 403)

    def test_post_succeeds(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, approved=True
        )
        rsvp_fields = self.rsvp_fields
        new_value = "XL"
        rsvp_fields["shirt_size"] = new_value
        rsvp = Rsvp(**self.rsvp_fields, user=self.user)
        rsvp.save()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse_lazy("rsvp:update", args=(rsvp.id,)), self.rsvp_fields
        )
        rsvp.refresh_from_db()

        self.assertRedirects(response, f"{reverse_lazy('status')}")
        self.assertEqual(rsvp.shirt_size, new_value)
