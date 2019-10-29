from django.contrib import admin
from django.urls import reverse_lazy

from shared import test_case


class UserAdminTestCase(test_case.SharedTestCase):
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
        self.assertEqual(response.status_code, 200)
