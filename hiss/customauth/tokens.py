from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


email_confirmation_generator = ConfirmationTokenGenerator()
