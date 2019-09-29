from django.contrib import admin
from django.urls import reverse_lazy

from shared import test_case


class UserAdminTestCase(test_case.SharedTestCase):
    def test_check_in_checks_in_users(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:user_user_changelist")
        self.client.post(
            change_url,
            {"action": "check_in", admin.ACTION_CHECKBOX_NAME: [self.user.pk]},
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.checked_in)

    def test_export_user_emails(self):
        self.client.force_login(self.admin)
        change_url = reverse_lazy("admin:user_user_changelist")
        response = self.client.post(
            change_url,
            {
                "action": "export_user_emails",
                admin.ACTION_CHECKBOX_NAME: [self.user.pk],
            },
            follow=True,
        )
        self.assertEquals(response.status_code, 200)
