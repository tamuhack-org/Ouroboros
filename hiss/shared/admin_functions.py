from django.core.mail import EmailMultiAlternatives, get_connection


def send_mass_html_mail(
    datatuple, fail_silently=False, user=None, password=None, connection=None
):
    """Send email to every recipient in datatuple.

    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient  in the recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    (from <a href="https://stackoverflow.com/a/10215091">this StackOverflow answer</a>
    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, "text/html")
        messages.append(message)
    return connection.send_messages(messages)
