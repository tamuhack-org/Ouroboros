from django.core.mail import get_connection, EmailMultiAlternatives
import threading

#create separate Threading class for mass emails
class MassEmailThread(threading.Thread):
    def __init__(self, subject, text_content, html_content, from_email, recipient_list, connection):
        threading.Thread.__init__(self)
        self.subject = subject
        self.text_content = text_content
        self.html_content = html_content
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.connection = connection
        self.result = 0  

    def run(self):
        email = EmailMultiAlternatives(self.subject, self.text_content, self.from_email, self.recipient_list)
        email.attach_alternative(self.html_content, "text/html")
        try:
            self.result = email.send(fail_silently=False, connection=self.connection)
        except Exception as e:
            print("Error sending email: ", e)
            self.result = 0

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, connection=None):
    """
    Sends each message in datatuple (subject, text_content, html_content, from_email, recipient_list).
    Returns the number of emails sent.
    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )

    threads = []

    for subject, text, html, from_email, recipient in datatuple:
        email_thread = MassEmailThread(subject, text, html, from_email, recipient, connection)
        email_thread.start()
        threads.append(email_thread)

    for thread in threads:
        thread.join()

    total_sent = sum(thread.result for thread in threads if thread.result)

    return total_sent