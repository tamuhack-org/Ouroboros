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
