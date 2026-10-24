"""Tests for the Unfold admin: list filters, action confirmation, and the dashboard."""

from datetime import timedelta

from django.apps import apps
from django.contrib import admin
from django.core import mail
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from application.constants import (
    ASIAN_EAST,
    FEMALE,
    MALE,
    NO_ANSWER,
    STATUS_ADMITTED,
    STATUS_CHECKED_IN,
    STATUS_CONFIRMED,
    STATUS_EXPIRED,
    STATUS_PENDING,
    STATUS_REJECTED,
)
from application.models import AdHocEmailBatch, Application
from shared import test_case
from team.models import Team
from user.models import User

CHANGELIST = "admin:application_application_changelist"


class UnfoldAdminTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.client.force_login(self.admin)
        self._user_count = 0

    def make_app(self, **overrides) -> Application:
        self._user_count += 1
        user = User.objects.create_user(
            email=f"applicant{self._user_count}@example.com", password=self.password
        )
        fields = {**self.application_fields, "user": user, "wave": self.wave1}
        fields.update(overrides)
        return Application.objects.create(**fields)

    def changelist_pks(self, params) -> set:
        response = self.client.get(reverse(CHANGELIST), params)
        self.assertEqual(response.status_code, 200)
        return {app.pk for app in response.context["cl"].queryset}


class ApplicationFilterTestCase(UnfoldAdminTestCase):
    """Every changelist filter must actually narrow the results (regression from PR #515)."""

    def test_status_filter_accepts_multiple_values(self):
        pending = self.make_app(status=STATUS_PENDING)
        admitted = self.make_app(status=STATUS_ADMITTED)
        self.make_app(status=STATUS_REJECTED)

        pks = self.changelist_pks(
            {"status__exact": [STATUS_PENDING, STATUS_ADMITTED]}
        )

        self.assertEqual(pks, {pending.pk, admitted.pk})

    def test_status_tab_filters_single_status(self):
        pending = self.make_app(status=STATUS_PENDING)
        self.make_app(status=STATUS_ADMITTED)

        self.assertEqual(self.changelist_pks({"status__exact": STATUS_PENDING}), {pending.pk})

    def test_gender_filter(self):
        male = self.make_app(gender=MALE)
        self.make_app(gender=FEMALE)

        self.assertEqual(self.changelist_pks({"gender__exact": MALE}), {male.pk})

    def test_grad_year_filter(self):
        year = timezone.now().year
        later = self.make_app(grad_year=year + 2)
        self.make_app(grad_year=year + 1)

        self.assertEqual(self.changelist_pks({"grad_year__exact": year + 2}), {later.pk})

    def test_school_filter(self):
        second = self.make_app(school=self.second_school)
        self.make_app(school=self.first_school)

        pks = self.changelist_pks({"school__id__exact": self.second_school.pk})

        self.assertEqual(pks, {second.pk})

    def test_race_filter(self):
        asian = self.make_app(race=[ASIAN_EAST])
        self.make_app(race=[NO_ANSWER])

        self.assertEqual(self.changelist_pks({"race": ASIAN_EAST}), {asian.pk})

    def test_deadline_proximity_filter(self):
        recent = self.make_app(confirmation_deadline=timezone.now() - timedelta(days=1))
        self.make_app(confirmation_deadline=timezone.now() - timedelta(days=10))

        self.assertEqual(self.changelist_pks({"deadline_days": "3"}), {recent.pk})

    def test_submitted_date_range_includes_whole_end_day(self):
        today = self.make_app()
        old = self.make_app()
        Application.objects.filter(pk=old.pk).update(
            datetime_submitted=timezone.now() - timedelta(days=10)
        )
        today_str = timezone.localdate().isoformat()

        pks = self.changelist_pks(
            {"datetime_submitted_from": today_str, "datetime_submitted_to": today_str}
        )

        self.assertEqual(pks, {today.pk})

    def test_status_tabs_highlight_only_the_current_tab(self):
        response = self.client.get(reverse(CHANGELIST), {"status__exact": STATUS_PENDING})

        tabs = response.context["tab_list"][0]["items"]
        active = [tab["title"] for tab in tabs if tab["active"]]
        self.assertEqual(active, ["Under review"])


class ActionConfirmationTestCase(UnfoldAdminTestCase):
    """Actions that email applicants must show a confirmation page first."""

    def setUp(self):
        super().setUp()
        self.app = self.make_app(status=STATUS_PENDING)

    def post_action(self, action_name, **extra):
        return self.client.post(
            reverse(CHANGELIST),
            {"action": action_name, "_selected_action": [self.app.pk], **extra},
        )

    def test_email_actions_render_confirmation_without_side_effects(self):
        for action_name in ("approve", "reject", "waitlist", "resend_confirmation"):
            with self.subTest(action=action_name):
                response = self.post_action(action_name)

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "admin/confirm_action.html")
                self.assertContains(response, self.app.user.email)
                self.assertContains(response, 'name="post" value="yes"')
                self.assertEqual(len(mail.outbox), 0)
                self.app.refresh_from_db()
                self.assertEqual(self.app.status, STATUS_PENDING)

    def test_confirmed_waitlist_updates_status_and_emails(self):
        self.post_action("waitlist", post="yes")

        self.app.refresh_from_db()
        self.assertEqual(self.app.status, STATUS_EXPIRED)
        self.assertEqual(len(mail.outbox), 1)

    def test_confirmed_action_redirects_to_next(self):
        change_url = reverse("admin:application_application_change", args=[self.app.pk])

        response = self.post_action("reject", post="yes", next=change_url)

        self.assertRedirects(response, change_url, fetch_redirect_response=False)

    def test_confirmed_action_ignores_external_next(self):
        response = self.post_action("reject", post="yes", next="https://evil.example.com/")

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("evil.example.com", response["Location"])

    def test_export_does_not_need_confirmation(self):
        response = self.post_action("export_application_emails")

        self.assertEqual(response["Content-Type"], "text/csv")

    def test_detail_buttons_render_confirmation_for_one_application(self):
        for name in ("approve_detail", "waitlist_detail", "reject_detail"):
            with self.subTest(button=name):
                response = self.client.get(
                    reverse(f"admin:application_application_{name}", args=[self.app.pk])
                )

                self.assertTemplateUsed(response, "admin/confirm_action.html")
                self.assertEqual(response.context["selected_pks"], [self.app.pk])
                self.assertEqual(
                    response.context["next_url"],
                    reverse("admin:application_application_change", args=[self.app.pk]),
                )
                self.assertEqual(len(mail.outbox), 0)

    def test_team_approve_confirms_then_approves_every_member(self):
        team = Team.objects.create()
        teammate = self.make_app(team=team)
        Application.objects.filter(pk=self.app.pk).update(team=team)
        team_url = reverse("admin:team_team_change", args=[team.pk])

        response = self.client.get(reverse("admin:team_team_approve_team", args=[team.pk]))

        self.assertTemplateUsed(response, "admin/confirm_action.html")
        self.assertEqual(set(response.context["selected_pks"]), {self.app.pk, teammate.pk})
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(
            response.context["form_url"],
            {
                "action": "approve",
                "_selected_action": response.context["selected_pks"],
                "post": "yes",
                "next": team_url,
            },
        )

        self.assertRedirects(response, team_url, fetch_redirect_response=False)
        self.assertEqual(
            set(Application.objects.filter(team=team).values_list("status", flat=True)),
            {STATUS_ADMITTED},
        )
        self.assertEqual(len(mail.outbox), 2)


class DashboardTestCase(UnfoldAdminTestCase):
    def get_dashboard(self, **params):
        response = self.client.get(reverse("admin:index"), params)
        self.assertEqual(response.status_code, 200)
        return response

    def test_status_cards_and_funnel_counts(self):
        for status in (STATUS_PENDING, STATUS_PENDING, STATUS_ADMITTED, STATUS_CONFIRMED, STATUS_CHECKED_IN):
            self.make_app(status=status)

        context = self.get_dashboard().context
        cards = {card["label"]: card["value"] for card in context["status_cards"]}
        funnel = {step["label"]: step["value"] for step in context["funnel"]}

        self.assertEqual(cards["Applied"], "5")
        self.assertEqual(cards["Under review"], "2")
        self.assertEqual(cards["Confirmed"], "1")
        self.assertEqual(funnel, {"Applied": "5", "Accepted": "3", "Confirmed": "2", "Checked in": "1"})
        self.assertEqual(context["pending_count"], 2)

    def test_gender_toggle_limits_to_accepted(self):
        self.make_app(gender=MALE, status=STATUS_ADMITTED)
        self.make_app(gender=FEMALE, status=STATUS_PENDING)
        self.make_app(gender=FEMALE, status=STATUS_REJECTED)

        def counts(response):
            return {row["label"]: row["value"] for row in response.context["gender_rows"]}

        everyone = counts(self.get_dashboard())
        accepted = counts(self.get_dashboard(gender_scope="accepted"))

        self.assertEqual((everyone["Male"], everyone["Female"]), ("1", "2"))
        self.assertEqual((accepted["Male"], accepted["Female"]), ("1", "0"))

    def test_empty_dashboard_renders(self):
        response = self.get_dashboard()

        self.assertContains(response, "No applications yet")

    def test_query_count_does_not_grow_with_applications(self):
        self.make_app()
        with CaptureQueriesContext(connection) as few:
            self.get_dashboard()

        for _ in range(10):
            self.make_app()
        with CaptureQueriesContext(connection) as many:
            self.get_dashboard()

        self.assertEqual(len(few), len(many))


class AdminSmokeTestCase(UnfoldAdminTestCase):
    def test_every_changelist_and_add_page_loads(self):
        registered = [model for model in apps.get_models() if admin.site.is_registered(model)]
        for model in registered:
            model_admin = admin.site.get_model_admin(model)
            opts = model_admin.opts
            with self.subTest(model=opts.label):
                url = reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")
                self.assertEqual(self.client.get(url).status_code, 200)

                if model_admin.has_add_permission(self.client.request().wsgi_request):
                    url = reverse(f"admin:{opts.app_label}_{opts.model_name}_add")
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_change_pages_load(self):
        app = self.make_app(team=Team.objects.create())
        batch = AdHocEmailBatch.objects.create(subject="Hi", html_template="<p>{{ first_name }}</p>")
        objects = [app, app.team, self.wave1, self.admin, batch]

        for obj in objects:
            opts = admin.site.get_model_admin(type(obj)).opts
            with self.subTest(model=opts.label):
                url = reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk])
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_email_history_is_read_only(self):
        batch = AdHocEmailBatch.objects.create(subject="Hi", html_template="<p>x</p>")

        add = self.client.get(reverse("admin:application_adhocemailbatch_add"))
        delete = self.client.post(
            reverse("admin:application_adhocemailbatch_delete", args=[batch.pk]), {"post": "yes"}
        )

        self.assertEqual(add.status_code, 403)
        self.assertEqual(delete.status_code, 403)
        self.assertTrue(AdHocEmailBatch.objects.filter(pk=batch.pk).exists())

    def test_ad_hoc_email_form_renders(self):
        session = self.client.session
        session["ad_hoc_email_app_ids"] = [str(self.make_app().pk)]
        session.save()

        response = self.client.get(reverse("admin:application_ad_hoc_email_form"))

        self.assertContains(response, 'name="subject"')
        self.assertContains(response, 'name="html_template"')
