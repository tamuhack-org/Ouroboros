from django.urls import reverse_lazy

from application.models import Application
from application.constants import STATUS_CHECKED_IN
from volunteer.models import BREAKFAST, FoodEvent
from volunteer.tests.test_case import TokenAuthTestCase
from volunteer.views import USER_NOT_CHECKED_IN_MSG


class CreateFoodEventViewTestCase(TokenAuthTestCase):
    def setUp(self):
        super().setUp()
        self.data_dict = {
            "email": self.email,
            "meal": BREAKFAST,
        }

    ### GET tests ###

    def test_get_fails_for_regular_user(self):
        self.create_active_wave()
        regular_user_token = self.get_token(self.email, self.password)

        response = self.client.get(
            reverse_lazy("volunteer:workshops"), data=self.data_dict, HTTP_AUTHORIZATION=regular_user_token
        )

        self.assertEqual(response.status_code, 403)
    
    def test_get_succeeds_for_volunteer(self):
        self.create_active_wave()

        app = Application.objects.create(**self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN)
        volunteer_token = self.get_volunteer_token()

        expected_output = {
            "dietaryRestrictions": "[Vegan, Vegetarian]",
            # app.save() has some logic that affects mealGroup, so we won't test it here
            "mealScans": [BREAKFAST],
        }

        app.dietary_restrictions = expected_output["dietaryRestrictions"]
        app.save() 
        app.refresh_from_db()


        self.client.post(
            reverse_lazy("volunteer:food"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=volunteer_token,
        )

        response = self.client.get(
            reverse_lazy("volunteer:food"), data=self.data_dict, HTTP_AUTHORIZATION=volunteer_token
        )

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json["dietaryRestrictions"], expected_output["dietaryRestrictions"])
        self.assertEqual(response_json["mealScans"], expected_output["mealScans"])
    

    ### POST tests ###

    def test_post_fails_for_regular_user(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        regular_user_token = self.get_token(self.email, self.password)

        response = self.client.post(
            reverse_lazy("volunteer:food"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=regular_user_token,
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(FoodEvent.objects.filter(user=self.user).exists())

    def test_post_succeeds_for_volunteer(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        volunteer_token = self.get_volunteer_token()

        response = self.client.post(
            reverse_lazy("volunteer:food"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=volunteer_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(FoodEvent.objects.filter(user=self.user).exists())

    def test_post_succeeds_for_admin(self):
        self.create_active_wave()
        Application.objects.create(
            **self.application_fields, wave=self.wave1, status=STATUS_CHECKED_IN
        )
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.post(
            reverse_lazy("volunteer:food"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(FoodEvent.objects.filter(user=self.user).exists())

    def test_post_fails_when_user_not_checked_in(self):
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        admin_token = self.get_token(self.admin_email, self.admin_password)

        response = self.client.post(
            reverse_lazy("volunteer:food"),
            data=self.data_dict,
            HTTP_AUTHORIZATION=admin_token,
        )

        self.assertEqual(response.status_code, 412)
        self.assertJSONEqual(response.content, {"error": USER_NOT_CHECKED_IN_MSG})
        self.assertFalse(FoodEvent.objects.filter(user=self.user).exists())
