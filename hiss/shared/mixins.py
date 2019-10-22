from django.contrib.auth import mixins
from django.shortcuts import redirect


class LoginRequiredAndAppliedMixin(mixins.UserPassesTestMixin):
    """
    Deny a request with a permission error if the user isn't logged in or hasn't applied.
    """

    def test_func(self) -> bool:
        # Ensure user is logged-in
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Ensure user has applied
        if not user.application_set.exists():
            return False
        return True

class TeamDoesNotExistMixin(mixins.UserPassesTestMixin):
    """
    Deny a request with a permission error if the user is already a member of a team
    """

    def handle_no_permission(self):
        return redirect("/status/")

    def test_func(self) -> bool:
        # Ensure the user is logged-in
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Ensure user has applied
        if not user.application_set.exists():
            return False

        # Ensure user doesn't have a team
        if user.team is not None:
            return False
        return True
