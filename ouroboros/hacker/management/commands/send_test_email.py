import enum

from django.contrib.sites import shortcuts as site_shortcuts
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from customauth.forms import PlaceholderPasswordResetForm
from django.http import HttpRequest
from django.conf import settings
from hacker.admin import send_application_approval_email, send_application_rejection_email

from customauth.tokens import email_confirmation_generator
from hacker.models import Hacker, Application, send_rsvp_creation_email, Wave

RESUME = SimpleUploadedFile("resume.pdf", b"dummy")
RESUME_FILE_DATA = {"resume": RESUME}


UNSUPPORTED_TEMPLATE_MSG = "Unsupported template name provided."


class Command(BaseCommand):
    help = "Sends a dummy email to the provided email address"

    def add_arguments(self, parser):
        parser.add_argument("dest_email", type=str, help="The destination email")
        parser.add_argument(
            "template_path",
            type=str,
            help="The path (starting from 'templates') to the template",
        )

    def create_hacker(self, **options) -> Hacker:
        dummy_hacker = Hacker.objects._create_user(options["dest_email"], "dummy_pass")
        print(dummy_hacker)
        return dummy_hacker

    def delete_hacker(self, **options):
        Hacker.objects.get(email=options["dest_email"]).delete()

    def handle(self, *args, **options):
        try:
            dummy_hacker: Hacker = self.create_hacker(**options)
            template_path = options["template_path"]

            if template_path == "emails/activate_email.html":
                curr_domain = "localhost"
                subject = "Confirm your email address!"
                context = {
                    "user": dummy_hacker,
                    "domain": curr_domain,
                    "uid": urlsafe_base64_encode(force_bytes(dummy_hacker.pk)),
                    "token": email_confirmation_generator.make_token(dummy_hacker),
                    "event_name": settings.EVENT_NAME,
                }
                dummy_hacker.email_html_hacker(template_path, context, subject)
            elif template_path.startswith("emails/application"):
                wave: Wave = Wave(start=timezone.now(), end=timezone.now())
                wave.save()
                application_fields = {
                    "first_name": "Kennedy",
                    "last_name": "Doe",
                    "major": "Computer Science",
                    "gender": "M",
                    "classification": "Fr",
                    "grad_year": "Other",
                    "num_hackathons_attended": 0,
                    "hacker": dummy_hacker,
                    "race": ["NA"],
                    "extra_links": "A",
                    "programming_joke": "B",
                    "unlimited_resource": "C",
                    "cool_prize": "D",
                    "adult": True,
                    "previous_attendant": False,
                    "additional_accommodations": "E",
                    "mlh_coc": True,
                    **RESUME_FILE_DATA,
                    "wave_id": wave.pk
                }
                app: Application = Application(**application_fields)
                app.save()
                if template_path == "emails/application/approved.html":
                    send_application_approval_email(app)
                elif template_path == "emails/application/created.html":
                    pass
                elif template_path == "emails/application/rejected.html":
                    send_application_rejection_email(app)
                else:
                    raise Exception(UNSUPPORTED_TEMPLATE_MSG)
            elif template_path.startswith("emails/rsvp"):
                wave: Wave = Wave(start=timezone.now(), end=timezone.now())
                wave.save()
                application_fields = {
                    "first_name": "Kennedy",
                    "last_name": "Doe",
                    "major": "Computer Science",
                    "gender": "M",
                    "classification": "Fr",
                    "grad_year": "Other",
                    "num_hackathons_attended": 0,
                    "hacker": dummy_hacker,
                    "race": ["NA"],
                    "extra_links": "A",
                    "programming_joke": "B",
                    "unlimited_resource": "C",
                    "cool_prize": "D",
                    "adult": True,
                    "previous_attendant": False,
                    "additional_accommodations": "E",
                    "mlh_coc": True,
                    **RESUME_FILE_DATA,
                    "wave_id": wave.pk
                }
                app: Application = Application(**application_fields)
                app.save()
                if template_path == "emails/rsvp/created.html":
                    send_rsvp_creation_email(dummy_hacker)
                elif template_path == "emails/rsvp/updated.html":
                    pass
                else:
                    raise Exception(UNSUPPORTED_TEMPLATE_MSG)
            elif template_path == "registration/password_reset_email.html":
                print(
                    "I can't figure out how to do this automatically. This will need to be tested by hand."
                )
            else:
                raise Exception(UNSUPPORTED_TEMPLATE_MSG)
        except Exception as e:
            print(e)
        finally:
            self.delete_hacker(**options)
