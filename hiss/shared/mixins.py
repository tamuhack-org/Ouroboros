from django.contrib.auth import mixins


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


class UserHasNoTeamMixin(mixins.UserPassesTestMixin):
    """
    Deny a request with a permission error if the user isn't logged in or if the user
    is already on another team.
    """

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


class UserHasTeamMixin(mixins.UserPassesTestMixin):
    """
    Deny a request with a permission error if the user isn't logged in or if the user
    is not currently on a team.
    """

    def test_func(self) -> bool:
        # Ensure the user is logged-in
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Ensure user has applied
        if not user.application_set.exists():
            return False

        # Ensure the user is already on a team
        if user.team is None:
            return False
        return True
