"""Intermediate confirmation page for admin actions that email people.

Works like Django's built-in `delete_selected`: the first POST renders a summary page,
and the page posts back to the same action with `post=yes` to actually run it.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from django.contrib.admin import ModelAdmin, helpers
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.http import url_has_allowed_host_and_scheme

PREVIEW_LIMIT = 50


@dataclass(frozen=True)
class Confirmation:
    title: str  # Formatted with {count} and {s}, e.g. "Approve {count} application{s}"
    message: str
    confirm_label: str
    icon: str
    variant: str = "primary"  # "primary" or "danger"


def is_confirmed(request: HttpRequest | None) -> bool:
    """Whether an action should run now.

    `request` is None when actions are called from management commands, which never
    need confirmation.
    """
    return request is None or request.POST.get("post") == "yes"


def render_confirmation(  # noqa: PLR0913
    request: HttpRequest,
    model_admin: ModelAdmin,
    *,
    confirmation: Confirmation,
    action: str,
    selected_pks: Iterable,
    recipients: list[tuple[str, str]],
    form_url: str,
    next_url: str = "",
    cancel_url: str = "",
) -> TemplateResponse:
    """Render the confirmation page for an action.

    `recipients` is a list of (name, email) pairs that will be emailed.
    """
    count = len(recipients)
    context = {
        **model_admin.admin_site.each_context(request),
        "title": confirmation.title.format(count=count, s="" if count == 1 else "s"),
        "confirmation": confirmation,
        "opts": model_admin.opts,
        "action": action,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "selected_pks": list(selected_pks),
        "recipient_count": count,
        "preview": recipients[:PREVIEW_LIMIT],
        "remaining": max(count - PREVIEW_LIMIT, 0),
        "form_url": form_url,
        "next_url": next_url,
        "cancel_url": cancel_url or form_url,
    }
    return TemplateResponse(request, "admin/confirm_action.html", context)


def redirect_to_next(request: HttpRequest | None) -> HttpResponseRedirect | None:
    """Send the user back to `next` after a confirmed action, if one was given."""
    if request is None:
        return None
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return HttpResponseRedirect(next_url)
    return None
