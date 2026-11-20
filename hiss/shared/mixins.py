from django.contrib.auth import mixins
from django.utils.text import capfirst


class LoginRequiredAndAppliedMixin(mixins.UserPassesTestMixin):
    """Deny a request with a permission error if the user isn't logged in or hasn't applied."""

    def test_func(self) -> bool:
        # Ensure user is logged-in
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Ensure user has applied
        return not user.application_set.exists()


class ListTitleMixin:
    """Title an admin list page like its sidebar link ("Applications") instead of
    Django's "Select application to change"."""

    list_title: str | None = None

    def changelist_view(self, request, extra_context=None):
        title = self.list_title or capfirst(self.opts.verbose_name_plural)
        return super().changelist_view(request, {"title": title, **(extra_context or {})})
