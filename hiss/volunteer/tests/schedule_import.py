from unittest import mock

import requests
from django.urls import reverse

from shared import test_case
from volunteer.models import ScheduleEvent
from volunteer.schedule_import import ScheduleImportError, import_schedule

FEED = [
    {
        "id": "evt1",
        "date": "2026-10-24T18:30:00.000Z",
        "eventName": "Intro to Git",
        "description": "",
        "location": "MSC 2400",
        "tags": [],
    },
    {
        "id": "evt2",
        "date": "2026-10-25T17:00:00.000Z",
        "eventName": "Lunch (Dominos)",
        "description": "Pizza",
        "location": "MSC 2401",
        "tags": [],
    },
    {"id": "bad", "date": "not a date", "eventName": "Skipped"},
]


def mock_feed(data=FEED):
    response = mock.Mock()
    response.json.return_value = data
    response.raise_for_status.return_value = None
    return mock.patch("volunteer.schedule_import.requests.get", return_value=response)


class ScheduleImportTestCase(test_case.SharedTestCase):
    def test_imports_valid_events(self):
        with mock_feed():
            created, updated = import_schedule()
        self.assertEqual((created, updated), (2, 0))
        git = ScheduleEvent.objects.get(external_id="evt1")
        self.assertEqual(git.name, "Intro to Git")
        self.assertEqual(git.location, "MSC 2400")
        self.assertEqual(git.start.isoformat(), "2026-10-24T18:30:00+00:00")
        self.assertFalse(ScheduleEvent.objects.filter(name="Skipped").exists())

    def test_reimport_updates_without_duplicates_and_keeps_admin_fields(self):
        with mock_feed():
            import_schedule()
        ScheduleEvent.objects.filter(external_id="evt2").update(
            category=ScheduleEvent.CATEGORY_FOOD, is_visible=False
        )
        changed = [{**FEED[0], "location": "MSC 2500"}, FEED[1]]
        with mock_feed(changed):
            created, updated = import_schedule()

        self.assertEqual((created, updated), (0, 2))
        self.assertEqual(ScheduleEvent.objects.count(), 2)
        self.assertEqual(
            ScheduleEvent.objects.get(external_id="evt1").location, "MSC 2500"
        )
        lunch = ScheduleEvent.objects.get(external_id="evt2")
        self.assertEqual(lunch.category, ScheduleEvent.CATEGORY_FOOD)
        self.assertFalse(lunch.is_visible)

    def test_network_error_raises(self):
        with (
            mock.patch(
                "volunteer.schedule_import.requests.get",
                side_effect=requests.ConnectionError("down"),
            ),
            self.assertRaises(ScheduleImportError),
        ):
            import_schedule()

    def test_non_list_response_raises(self):
        with mock_feed({"error": "nope"}), self.assertRaises(ScheduleImportError):
            import_schedule()

    def test_admin_button_imports(self):
        self.client.force_login(self.admin)
        url = reverse("admin:volunteer_scheduleevent_import_from_website")
        with mock_feed():
            response = self.client.get(url)
        self.assertRedirects(
            response, reverse("admin:volunteer_scheduleevent_changelist")
        )
        self.assertEqual(ScheduleEvent.objects.count(), 2)

    def test_admin_button_requires_staff(self):
        self.client.force_login(self.user)
        url = reverse("admin:volunteer_scheduleevent_import_from_website")
        with mock_feed() as get:
            self.client.get(url)
        get.assert_not_called()
        self.assertEqual(ScheduleEvent.objects.count(), 0)
