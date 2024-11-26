from celery import shared_task
from django.core.mail import get_connection, EmailMultiAlternatives

@shared_task
def send_mass_html_mail_task(datatuple, fail_silently=False, user=None, password=None):
    """
    Celery task to send multiple HTML emails given a datatuple of 
    (subject, text_content, html_content, from_email, recipient_list).
    """
    connection = get_connection(
        username=user, password=password, fail_silently=fail_silently
    )
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, "text/html")
        messages.append(message)
    
    return connection.send_messages(messages)
