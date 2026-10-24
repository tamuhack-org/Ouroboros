"""Django Unfold admin configuration.

See https://unfoldadmin.com/docs/configuration/settings/
"""

from django.templatetags.static import static
from django.urls import reverse, reverse_lazy

from .customization import EVENT_NAME, EVENT_YEAR, ORGANIZER_NAME

APPLICATION_CHANGELIST = reverse_lazy("admin:application_application_changelist")


def _status_tab(title: str, status: str) -> dict:
    # Links are callables so URLs resolve per request, not at settings import time.
    return {
        "title": title,
        "link": lambda request: (
            f"{reverse('admin:application_application_changelist')}?status__exact={status}"
        ),
    }


UNFOLD = {
    "SITE_TITLE": f"{ORGANIZER_NAME} Admin",
    "SITE_HEADER": ORGANIZER_NAME,
    "SITE_SUBHEADER": f"{EVENT_NAME} {EVENT_YEAR}",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("th_logo.svg"),
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "type": "image/svg+xml",
            "href": lambda request: static("th_logo.svg"),
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "ENVIRONMENT": "shared.admin_callbacks.environment_callback",
    "DASHBOARD_CALLBACK": "shared.admin_callbacks.dashboard_callback",
    "COLORS": {
        # Built around TAMUhack pink #F27B93 (primary-500). 600 is darkened so white
        # text on buttons and pink text on tinted backgrounds meet WCAG AA (4.5:1+).
        "primary": {
            "50": "oklch(97.5% 0.012 8.71)",
            "100": "oklch(94.8% 0.026 8.71)",
            "200": "oklch(90.0% 0.050 8.71)",
            "300": "oklch(84.0% 0.088 8.71)",
            "400": "oklch(78.0% 0.120 8.71)",
            "500": "oklch(72.4% 0.147 8.71)",
            "600": "oklch(55.5% 0.180 9.60)",
            "700": "oklch(51.5% 0.165 10.49)",
            "800": "oklch(44.5% 0.138 11.38)",
            "900": "oklch(38.5% 0.110 12.27)",
            "950": "oklch(28.0% 0.080 12.71)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "space_dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Applicants",
                "separator": True,
                "items": [
                    {
                        "title": "Applications",
                        "icon": "description",
                        "link": APPLICATION_CHANGELIST,
                        "badge": "shared.admin_callbacks.pending_badge",
                        "badge_variant": "primary",
                    },
                    {
                        "title": "Teams",
                        "icon": "groups",
                        "link": reverse_lazy("admin:team_team_changelist"),
                    },
                    {
                        "title": "Waves",
                        "icon": "waves",
                        "link": reverse_lazy("admin:application_wave_changelist"),
                    },
                    {
                        "title": "Email history",
                        "icon": "forward_to_inbox",
                        "link": reverse_lazy(
                            "admin:application_adhocemailbatch_changelist"
                        ),
                    },
                ],
            },
            {
                "title": "Event",
                "separator": True,
                "items": [
                    {
                        "title": "Food",
                        "icon": "restaurant",
                        "link": reverse_lazy("admin:volunteer_foodevent_changelist"),
                    },
                    {
                        "title": "Workshops",
                        "icon": "co_present",
                        "link": reverse_lazy(
                            "admin:volunteer_workshopevent_changelist"
                        ),
                    },
                ],
            },
            {
                "title": "People & Access",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:user_user_changelist"),
                    },
                    {
                        "title": "Groups",
                        "icon": "shield_person",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": "API tokens",
                        "icon": "key",
                        "link": reverse_lazy("admin:authtoken_tokenproxy_changelist"),
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["application.application"],
            "items": [
                {
                    "title": "All",
                    "link": APPLICATION_CHANGELIST,
                    # The bare changelist link would otherwise match every status tab.
                    "active": lambda request: "status__exact" not in request.GET,
                },
                _status_tab("Under review", "P"),
                _status_tab("Admitted", "A"),
                _status_tab("Confirmed", "C"),
                _status_tab("Waitlisted", "E"),
                _status_tab("Checked in", "I"),
                _status_tab("Rejected", "R"),
            ],
        },
    ],
}
