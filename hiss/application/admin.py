# pylint: disable=C0330
import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from django.core.validators import EMPTY_VALUES
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import Template, TemplateSyntaxError
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, strip_tags
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    DropdownFilter,
    MultipleChoicesDropdownFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
)
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.utils import parse_date_str
from unfold.widgets import (
    UnfoldAdminFileFieldWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminTextInputWidget,
)

from application.constants import (
    RACES,
    STATUS_ADMIN_LABELS,
    STATUS_ADMIN_VARIANTS,
    STATUS_ADMITTED,
    STATUS_EXPIRED,
    STATUS_REJECTED,
)
from application.models import (
    AdHocEmailBatch,
    Application,
    Wave,
)
from application.tasks import bg_dispatch_ad_hoc_emails, bg_dispatch_send_update_emails
from hiss.settings.customization import EVENT_TIMEZONE
from shared.admin_confirm import (
    Confirmation,
    is_confirmed,
    redirect_to_next,
    render_confirmation,
)
from shared.admin_functions import send_mass_html_mail


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = "__all__"  # noqa: DJ007
        widgets = {
            "gender": UnfoldAdminRadioSelectWidget,
            "grad_year": UnfoldAdminRadioSelectWidget,
            "status": UnfoldAdminRadioSelectWidget,
        }


class AdHocEmailForm(forms.Form):
    """Renders the ad hoc email inputs with Unfold styling (the view reads POST directly)."""

    subject = forms.CharField(
        widget=UnfoldAdminTextInputWidget(attrs={"placeholder": "Email subject line"})
    )
    html_template = forms.FileField(
        label="HTML template",
        help_text="Upload a UTF-8 encoded .html file.",
        widget=UnfoldAdminFileFieldWidget(attrs={"accept": ".html,.htm"}),
    )


def format_deadline_date(deadline: datetime) -> str:
    """Format as e.g. "January 5, 2026" (portable alternative to "%B %-d, %Y")."""
    return f"{deadline:%B} {deadline.day}, {deadline:%Y}"


def format_deadline_time(deadline: datetime) -> str:
    """Format as e.g. "11:59 PM CST" (portable alternative to "%-I:%M %p %Z")."""
    return f"{deadline.hour % 12 or 12}:{deadline:%M %p %Z}"


def build_approval_email(
    application: Application, confirmation_deadline: datetime
) -> tuple[str, str, str, None, list[str]]:
    """Create an email data tuple indicating that a user's application has been approved.

    Args:
        application (Application): The application object containing user
        details.
        confirmation_deadline (timezone.datetime): The deadline for
        the user to confirm their application.


    Returns: tuple: A tuple containing the email subject, plain text message,
    HTML message, from email (None), and a list of recipient email addresses.

    """
    subject = (
        f"ACTION REQUIRED: One last step for your {settings.EVENT_NAME} application!"
    )

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "confirmation_deadline": format_deadline_date(confirmation_deadline),
        "confirmation_time": format_deadline_time(confirmation_deadline),
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_message = render_to_string("application/emails/approved.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def build_rejection_email(application: Application) -> tuple[str, str, str, None, list[str]]:
    """Create email indicating a `User` is rejected.

    Return type is (subject, message, html_message, from_email, [to_email])
    """
    subject = f"Regarding your {settings.EVENT_NAME} application"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_message = render_to_string("application/emails/rejected.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


# Confirmation copy for every action that emails applicants
CONFIRMATIONS = {
    "approve": Confirmation(
        title="Approve {count} application{s}",
        message=(
            "Each applicant will be emailed an acceptance with a confirmation deadline "
            "based on their wave's RSVP window."
        ),
        confirm_label="Approve and send emails",
        icon="check_circle",
    ),
    "reject": Confirmation(
        title="Reject {count} application{s}",
        message="Each applicant will be emailed a rejection. This cannot be undone.",
        confirm_label="Reject and send emails",
        icon="cancel",
        variant="danger",
    ),
    "waitlist": Confirmation(
        title="Waitlist {count} application{s}",
        message="Each applicant will be emailed that they are on the waitlist, with day-of check-in details.",
        confirm_label="Waitlist and send emails",
        icon="hourglass_top",
    ),
    "resend_confirmation": Confirmation(
        title="Resend status email to {count} applicant{s}",
        message=(
            "Each applicant will be emailed an update matching their current status. "
            "Applicants still under review get a “still reviewing” email."
        ),
        confirm_label="Send emails",
        icon="forward_to_inbox",
    ),
}


def confirm_application_action(
    modeladmin, request: HttpRequest, queryset: QuerySet[Application], action_name: str,
    *, next_url: str = "",
) -> TemplateResponse:
    """Render the confirmation page for an email-sending application action."""
    applications = list(queryset.select_related("user"))
    changelist_url = reverse("admin:application_application_changelist")
    return render_confirmation(
        request,
        modeladmin,
        confirmation=CONFIRMATIONS[action_name],
        action=action_name,
        selected_pks=[app.pk for app in applications],
        recipients=[
            (f"{app.first_name} {app.last_name}", app.user.email) for app in applications
        ],
        # From the changelist, post back to the same (filtered) URL; from a detail
        # page, post to the changelist and return to the detail page afterwards.
        form_url=changelist_url if next_url else request.get_full_path(),
        next_url=next_url,
        cancel_url=next_url,
    )


def notify(modeladmin, request: HttpRequest | None, message: str) -> None:
    if modeladmin is not None and request is not None:
        modeladmin.message_user(request, message, messages.SUCCESS)


def pluralize(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


@admin.action(description="Approve selected applications")
def approve(
    modeladmin, request: HttpRequest, queryset: QuerySet[Application]
) -> HttpResponse | None:
    """Approve selected Applications.

    Sets the value of the `approved` field for the selected `Application`s to `True`, creates an RSVP deadline for
    each user based on how many days each wave gives to RSVP, and then emails all of the users to inform them that
    their applications have been approved.
    """
    if not is_confirmed(request):
        return confirm_application_action(modeladmin, request, queryset, "approve")

    tz = ZoneInfo(EVENT_TIMEZONE)
    today_end = (
        timezone.now()
        .astimezone(tz)
        .replace(hour=23, minute=59, second=59, microsecond=0)
    )
    apps = queryset.select_related("wave", "user")

    to_update = []
    email_tuples = []

    for app in apps:
        deadline = today_end + timedelta(days=app.wave.num_days_to_rsvp)
        app.status = STATUS_ADMITTED
        app.confirmation_deadline = deadline

        to_update.append(app)
        email_tuples.append(build_approval_email(app, deadline))

    with transaction.atomic():
        Application.objects.bulk_update(to_update, ["status", "confirmation_deadline"])

    send_mass_html_mail(email_tuples)
    notify(modeladmin, request, f"Approved {pluralize(len(to_update), 'application')}.")
    return redirect_to_next(request)


@admin.action(description="Reject selected applications")
def reject(
    modeladmin, request: HttpRequest, queryset: QuerySet[Application]
) -> HttpResponse | None:
    """Set the value of the `approved` field for the selected `Application`s to `False`."""
    if not is_confirmed(request):
        return confirm_application_action(modeladmin, request, queryset, "reject")

    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            application.status = STATUS_REJECTED
            email_tuples.append(build_rejection_email(application))
            application.save()
    send_mass_html_mail(email_tuples)
    notify(modeladmin, request, f"Rejected {pluralize(len(email_tuples), 'application')}.")
    return redirect_to_next(request)


def build_waitlist_expired_email(
    application: Application,
) -> tuple[str, str, str, None, list[str]]:
    """Create an email for users whose applications expired (didn't confirm by deadline).

    Args:
        application (Application): The application object containing user details.

    Returns:
        A tuple representing the email to send.
    """
    subject = f"Update/next steps on your {settings.EVENT_NAME} application status"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
        "event_waitlist_checkin": settings.EVENT_WAITLIST_CHECKIN_DATETIME,
    }
    html_message = render_to_string("application/emails/waitlist-expired.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def build_waitlist_manual_email(
    application: Application,
) -> tuple[str, str, str, None, list[str]]:
    """Create an email for users who are manually waitlisted by admin.

    Args:
        application (Application): The application object containing user details.

    Returns:
        A tuple representing the email to send.
    """
    subject = f"Update/next steps on your {settings.EVENT_NAME} application status"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
        "event_waitlist_checkin": settings.EVENT_WAITLIST_CHECKIN_DATETIME,
    }
    html_message = render_to_string("application/emails/waitlist-manual.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


@admin.action(description="Waitlist selected applications")
def waitlist(
    modeladmin, request: HttpRequest, queryset: QuerySet[Application]
) -> HttpResponse | None:
    """Set the status of selected Applications to waitlisted (expired) and send waitlist emails."""
    if not is_confirmed(request):
        return confirm_application_action(modeladmin, request, queryset, "waitlist")

    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            application.status = STATUS_EXPIRED
            email_tuples.append(build_waitlist_manual_email(application))
            application.save()
    send_mass_html_mail(email_tuples)
    notify(modeladmin, request, f"Waitlisted {pluralize(len(email_tuples), 'application')}.")
    return redirect_to_next(request)


@admin.action(description="Resend status email to selected applicants")
def resend_confirmation(
    modeladmin, request: HttpRequest, queryset: QuerySet[Application]
) -> HttpResponse | None:
    """Resends the confirmation email to the selected applications.

    If the application is still pending, sends a 'still reviewing' email instead.
    """
    if not is_confirmed(request):
        return confirm_application_action(
            modeladmin, request, queryset, "resend_confirmation"
        )

    app_ids = [str(pk) for pk in queryset.values_list("pk", flat=True)]
    bg_dispatch_send_update_emails.enqueue(app_ids)

    modeladmin.message_user(request, f"Enqueued {len(app_ids)} email tasks.")
    return redirect_to_next(request)


@admin.action(description="Export emails of selected applicants (CSV)")
def export_application_emails(
    _modeladmin, _request: HttpRequest, queryset: QuerySet[Application]
):
    """Export the emails related to the selected `Application`s to a CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    writer.writerow(["email", "shirt_size"])
    for instance in queryset.select_related("user"):
        writer.writerow([instance.user.email, instance.shirt_size])

    return response


@admin.action(description="Send ad hoc email to selected applicants")
def send_ad_hoc_emails(
    _modeladmin, request: HttpRequest, queryset: QuerySet[Application]
) -> HttpResponseRedirect:
    """Redirect to ad hoc email form with selected application IDs."""
    selected_ids = [str(pk) for pk in queryset.values_list("pk", flat=True)]
    if not selected_ids:
        messages.error(request, "No applications selected.")
        return HttpResponseRedirect(reverse("admin:application_application_changelist"))
    request.session["ad_hoc_email_app_ids"] = selected_ids
    return HttpResponseRedirect(reverse("admin:application_ad_hoc_email_form"))


class RaceFilter(DropdownFilter):
    title = "Race"
    parameter_name = "race"

    def lookups(self, request: HttpRequest, model_admin) -> list[tuple[str, str]]:
        return RACES

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(race__contains=self.value())
        return queryset


class ConfirmationDeadlineProximityFilter(DropdownFilter):
    """Filter applications by how recently their confirmation deadline passed."""

    title = "Deadline within days"
    parameter_name = "deadline_days"

    def lookups(self, request: HttpRequest, model_admin) -> list[tuple[str, str]]:
        return [
            ("3", "Past 3 days"),
            ("5", "Past 5 days"),
            ("7", "Past 7 days"),
            ("14", "Past 14 days"),
            ("30", "Past 30 days"),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        query_string = self.value()
        if query_string not in EMPTY_VALUES:
            days = int(query_string)
            cutoff = timezone.now() - timedelta(days=days)
            return queryset.filter(confirmation_deadline__gt=cutoff)
        return queryset


class InclusiveDateRangeFilter(RangeDateFilter):
    """Date range over a datetime field that includes the whole "to" day.

    Unfold compares the datetime directly to the date (midnight), which would drop
    everything submitted later on the end day.
    """

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        filters = {}
        for suffix, lookup in (("_from", "gte"), ("_to", "lte")):
            value = self.used_parameters.get(f"{self.parameter_name}{suffix}")
            if value not in EMPTY_VALUES and (parsed := parse_date_str(value)):
                filters[f"{self.parameter_name}__date__{lookup}"] = parsed
        return queryset.filter(**filters)


class RelatedOnlyDropdownFilter(RelatedDropdownFilter, RelatedOnlyFieldListFilter):
    """Dropdown listing only related objects that are in use (e.g. schools with applicants)."""


class ApplicationAdminInline(TabularInline):
    model = Application
    fields = (
        "status_label",
        "is_captain",
        "school_name",
        "level",
        "grad_year_short",
        "resume_link",
        "links",
        "gender_short",
        "race_short",
        "short_answer",
        "age",
    )
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    @display(description="Status")
    def status_label(self, obj: Application) -> str:
        # Inline readonly fields ignore @display(label=...), so render the pill directly
        return render_to_string(
            "unfold/helpers/label.html",
            {
                "text": STATUS_ADMIN_LABELS.get(obj.status, obj.get_status_display()),
                "type": STATUS_ADMIN_VARIANTS.get(obj.status),
            },
        )

    @display(description="School")
    def school_name(self, obj: Application) -> str:
        return obj.school.name if obj.school else obj.school_other or "-"

    @display(description="Level")
    def level(self, obj: Application) -> str:
        return obj.get_level_of_study_display()

    @display(description="Grad year")
    def grad_year_short(self, obj: Application) -> int:
        return obj.grad_year

    @display(description="Gender")
    def gender_short(self, obj: Application) -> str:
        return obj.get_gender_display()

    @display(description="Race")
    def race_short(self, obj: Application) -> str:
        return str(obj.get_race_display())

    @display(description="Links")
    def links(self, obj: Application) -> str:
        return obj.extra_links or "-"

    @display(description="Short answer")
    def short_answer(self, obj: Application) -> str:
        return obj.misc_short_answer or "-"

    @admin.display(description="Resume")
    def resume_link(self, obj):
        if not obj.resume:
            return "-"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">View</a>',
            obj.resume.url,
        )

    def has_add_permission(self, request, obj=None):
        return False


class ApplicationAdmin(ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    list_select_related = ["school", "user", "wave"]
    search_fields = ["first_name", "last_name", "user__email"]
    search_help_text = "Search by first name, last name, or email"

    form = ApplicationAdminForm
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = True
    list_fullwidth = True

    readonly_fields = [
        "datetime_submitted",
        "user",
        # "is_adult",
        "gender",
        "race",
        "major",
        "school",
        "grad_year",
        "num_hackathons_attended",
        "dietary_restrictions",
        "extra_links",
        # "address",
        # "question2",
        # "question3",
        "notes",
        "misc_short_answer",
        "is_a_walk_in",
    ]
    list_filter = (
        ("status", MultipleChoicesDropdownFilter),
        ("school", RelatedOnlyDropdownFilter),
        ("gender", ChoicesDropdownFilter),
        RaceFilter,
        ("major", ChoicesDropdownFilter),
        ("grad_year", ChoicesDropdownFilter),
        ("level_of_study", ChoicesDropdownFilter),
        ("num_hackathons_attended", ChoicesDropdownFilter),
        ("wares", ChoicesDropdownFilter),
        ("shirt_size", ChoicesDropdownFilter),
        ("accessibility_requirements", ChoicesDropdownFilter),
        ("datetime_submitted", InclusiveDateRangeFilter),
        ConfirmationDeadlineProximityFilter,
    )
    # The dashboard links to "?o=5" (oldest first); keep "submitted" fifth.
    list_display = (
        "applicant",
        "school_name",
        "status_label",
        "grad_year_short",
        "submitted",
        "accommodations",
    )
    fieldsets = [
        (
            "Overview",
            {
                "classes": ["tab"],
                "fields": [
                    "status",
                    "confirmation_deadline",
                    "team",
                    "user",
                    "datetime_submitted",
                    "is_a_walk_in",
                ],
            },
        ),
        (
            "Personal",
            {
                "classes": ["tab"],
                "fields": [
                    "first_name",
                    "last_name",
                    "tamu_email",
                    "age",
                    "phone_number",
                    "country",
                    "extra_links",
                    # "question2",
                    # "question3",
                    "resume",
                ],
            },
        ),
        (
            "Demographics",
            {
                "classes": ["tab"],
                "fields": [
                    "school",
                    "school_other",
                    "major",
                    "major_other",
                    "gender",
                    "gender_other",
                    "race",
                    "race_other",
                    "grad_year",
                    "level_of_study",
                    "num_hackathons_attended",
                ],
            },
        ),
        (
            "Logistics",
            {
                "classes": ["tab"],
                "fields": [
                    "wares",
                    "shirt_size",
                    "dietary_restrictions",
                    "meal_group",
                    "additional_accommodations",
                    # "address",
                    "emergency_contact_name",
                    "emergency_contact_relationship",
                    "emergency_contact_phone",
                    "emergency_contact_email",
                ],
            },
        ),
        (
            "Misc",
            {
                "classes": ["tab"],
                "fields": [
                    "notes",
                    "misc_short_answer",
                    "is_adult",
                    "accessibility_requirements",
                ],
            },
        ),
    ]
    list_per_page = 100

    actions = [
        approve,
        reject,
        waitlist,
        export_application_emails,
        resend_confirmation,
        send_ad_hoc_emails,
    ]
    actions_detail = ["approve_detail", "waitlist_detail", "reject_detail"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "ad-hoc-email/",
                self.admin_site.admin_view(self.ad_hoc_email_view),
                name="application_ad_hoc_email_form",
            ),
        ]
        return custom_urls + urls

    def ad_hoc_email_view(self, request: HttpRequest) -> HttpResponse:
        """Router for ad hoc email form GET/POST."""
        if request.method == "POST":
            return self._process_ad_hoc_emails(request)
        return self._render_ad_hoc_email_form(request)

    def _render_ad_hoc_email_form(
        self, request: HttpRequest, error: str | None = None
    ) -> HttpResponse:
        """Render the ad hoc email form."""
        app_ids = request.session.get("ad_hoc_email_app_ids", [])
        if not app_ids:
            messages.error(request, "No applications selected. Please select applications first.")
            return HttpResponseRedirect(reverse("admin:application_application_changelist"))

        context = {
            **self.admin_site.each_context(request),
            "title": "Send ad hoc email",
            "opts": self.opts,
            "app_count": len(app_ids),
            "error": error,
            "form": AdHocEmailForm(initial={"subject": request.POST.get("subject", "")}),
        }
        return TemplateResponse(
            request, "admin/application/ad_hoc_email_form.html", context
        )

    def _process_ad_hoc_emails(self, request: HttpRequest) -> HttpResponse:
        """Handle POST: validate and enqueue ad hoc emails."""
        app_ids = request.session.get("ad_hoc_email_app_ids", [])
        if not app_ids:
            messages.error(request, "No applications selected. Please select applications first.")
            return HttpResponseRedirect(reverse("admin:application_application_changelist"))

        subject = request.POST.get("subject", "").strip()
        html_file = request.FILES.get("html_template")

        # Validation
        if not subject:
            return self._render_ad_hoc_email_form(request, error="Subject is required.")
        if not html_file:
            return self._render_ad_hoc_email_form(request, error="HTML template file is required.")

        # Read and decode HTML template
        try:
            html_content = html_file.read().decode("utf-8")
        except UnicodeDecodeError:
            return self._render_ad_hoc_email_form(
                request, error="Invalid file encoding. Please upload a UTF-8 encoded HTML file."
            )

        # Validate template syntax
        try:
            Template(html_content)
        except TemplateSyntaxError as e:
            return self._render_ad_hoc_email_form(
                request, error=f"Template syntax error: {e}"
            )

        # Create batch and enqueue tasks
        batch = AdHocEmailBatch.objects.create(
            subject=subject,
            html_template=html_content,
        )
        bg_dispatch_ad_hoc_emails.enqueue(str(batch.id), app_ids)

        # Clear session data
        del request.session["ad_hoc_email_app_ids"]

        messages.success(
            request, f"Successfully enqueued {len(app_ids)} ad hoc email tasks."
        )
        return HttpResponseRedirect(reverse("admin:application_application_changelist"))

    def _confirm_single(self, request: HttpRequest, object_id: str, action_name: str):
        queryset = self.get_queryset(request).filter(pk=object_id)
        change_url = reverse("admin:application_application_change", args=[object_id])
        return confirm_application_action(
            self, request, queryset, action_name, next_url=change_url
        )

    @action(description="Approve", icon="check_circle", variant=ActionVariant.PRIMARY)
    def approve_detail(self, request: HttpRequest, object_id: str):
        return self._confirm_single(request, object_id, "approve")

    @action(description="Waitlist", icon="hourglass_top")
    def waitlist_detail(self, request: HttpRequest, object_id: str):
        return self._confirm_single(request, object_id, "waitlist")

    # Not filled red here: the confirmation page carries the danger styling.
    @action(description="Reject", icon="cancel")
    def reject_detail(self, request: HttpRequest, object_id: str):
        return self._confirm_single(request, object_id, "reject")

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    @display(description="Applicant", header=True, ordering="last_name")
    def applicant(self, obj: Application) -> list[str]:
        initials = f"{obj.first_name[:1]}{obj.last_name[:1]}".upper()
        return [f"{obj.first_name} {obj.last_name}", obj.user.email, initials]

    @display(description="Status", ordering="status", label=STATUS_ADMIN_VARIANTS)
    def status_label(self, obj: Application) -> tuple[str, str]:
        return obj.status, STATUS_ADMIN_LABELS.get(obj.status, obj.get_status_display())

    @display(description="School", ordering="school__name")
    def school_name(self, obj: Application) -> str:
        return obj.school.name if obj.school else obj.school_other or "-"

    @display(description="Grad year", ordering="grad_year")
    def grad_year_short(self, obj: Application) -> int:
        return obj.grad_year

    @display(description="Submitted", ordering="datetime_submitted")
    def submitted(self, obj: Application) -> str:
        submitted = timezone.localtime(obj.datetime_submitted)
        return f"{submitted:%b} {submitted.day}, {submitted.hour % 12 or 12}:{submitted:%M %p}"

    @display(description="Accommodations", label={"Requested": "warning"})
    def accommodations(self, obj: Application) -> str | None:
        return "Requested" if obj.additional_accommodations else None

    @staticmethod
    def user_email(obj: Application) -> str:
        return obj.user.email

    @staticmethod
    @display(description="Walk-in wave", boolean=True)
    def is_a_walk_in(obj: Application) -> bool:
        return obj.wave.is_walk_in_wave


class WaveAdmin(ModelAdmin):
    list_display = ("start", "end", "num_days_to_rsvp", "walk_in")

    @display(description="Walk-in", label={True: "info"})
    def walk_in(self, obj: Wave) -> tuple[bool, str] | None:
        return (True, "Walk-in") if obj.is_walk_in_wave else None


class AdHocEmailBatchAdmin(ModelAdmin):
    """Read-only history of ad hoc emails sent from the Applications admin."""

    list_display = ("subject", "created_at")
    search_fields = ("subject",)
    ordering = ("-created_at",)
    fields = ("subject", "created_at", "template_source")
    readonly_fields = fields

    @display(description="HTML template")
    def template_source(self, obj: AdHocEmailBatch) -> str:
        return format_html(
            '<pre class="overflow-auto text-xs" style="max-height: 32rem; white-space: pre-wrap;">{}</pre>',
            obj.html_template,
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Wave, WaveAdmin)
admin.site.register(AdHocEmailBatch, AdHocEmailBatchAdmin)
