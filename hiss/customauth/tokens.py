from django.contrib.auth import tokens
from django.utils import six


class ConfirmationTokenGenerator(tokens.PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


email_confirmation_generator = ConfirmationTokenGenerator()
