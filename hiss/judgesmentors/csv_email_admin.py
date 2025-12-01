import csv
import io
import json
from io import BytesIO

import pyqrcode
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import strip_tags

from judgesmentors.models import STATUS_CONFIRMED, Judge, Mentor
from shared.admin_functions import send_mass_html_mail

User = get_user_model()


class CSVEmailAdminView:
    """Lightweight CSV to Email admin interface - no database storage"""

    def normalize_row(self, row):
        """Normalize a CSV row into standardized data format"""
        print(f"Processing row: {row}")
        is_faculty = str(row.get("is_faculty", "")).lower() in ["yes", "true", "1", "y"]

        return {
            "name": row.get("name", "").strip(),
            "email": row.get("email", "").strip(),
            "phone": row.get("phone", "").strip(),
            "tshirt_size": row.get("tshirt_size", "M").upper(),
            "is_faculty": is_faculty,
            "track": row.get("track", "SW").upper(),
            "additional_info": row.get("additional_info", "").strip(),
        }

    def get_urls(self):
        return [
            path(
                "judges/",
                staff_member_required(
                    lambda request: self.csv_email_view(request, "judges")
                ),
                name="csv_judge_emails",
            ),
            path(
                "mentors/",
                staff_member_required(
                    lambda request: self.csv_email_view(request, "mentors")
                ),
                name="csv_mentor_emails",
            ),
            path(
                "judges/process/",
                staff_member_required(self.process_judges_csv),
                name="process_judges_csv",
            ),
            path(
                "mentors/process/",
                staff_member_required(self.process_mentors_csv),
                name="process_mentors_csv",
            ),
        ]

    def csv_email_view(self, request, user_type):
        """Display the CSV upload and email interface for judges or mentors"""
        if user_type not in ["judges", "mentors"]:
            return JsonResponse({"error": "Invalid user type"}, status=400)

        context = {
            "title": f"{user_type.title()[:-1]} CSV Email System",
            "type": user_type,
            "opts": {"app_label": "judgesmentors", "model_name": user_type[:-1]},
        }
        return render(request, "admin/csv_email_interface.html", context)

    def process_judges_csv(self, request):  # noqa: PLR0911
        """Process judges CSV and send emails - no database storage"""
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)

        csv_file = request.FILES.get("csv_file")
        email_type = request.POST.get("email_type", "interest")

        if not csv_file:
            return JsonResponse({"error": "No CSV file provided"}, status=400)

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            # Print CSV content to console
            print("=== CSV UPLOAD - JUDGES ===")
            print(f"File: {csv_file.name}")
            print(f"Size: {csv_file.size} bytes")
            print(f"Email type: {email_type}")
            print("CSV Content:")

            # Reset for reading again
            io_string.seek(0)
            csv_content = io_string.getvalue()
            print(csv_content)
            print("=== END CSV CONTENT ===")

            # Reset for processing
            io_string.seek(0)
            reader = csv.DictReader(io_string)

            # Store judges data in memory only
            judges_data = []
            processed_count = 0

            for row in reader:
                judge_data = self.normalize_row(row)
                judges_data.append(judge_data)
                processed_count += 1

            # Send emails
            if processed_count > 0:
                email_tuples = []

                for judge_data in judges_data:
                    if email_type == "interest":
                        email_tuple = self.build_judge_interest_email(judge_data)
                        email_tuples.append(email_tuple)
                    else:  # confirmation
                        email_obj = self.build_judge_confirmation_email(judge_data)
                        email_obj.send()

                if email_type == "interest" and email_tuples:
                    send_mass_html_mail(email_tuples)
                    return JsonResponse(
                        {
                            "success": True,
                            "message": f"Successfully sent {email_type} emails to {len(email_tuples)} judges!",
                        }
                    )
                if email_type == "confirmation":
                    return JsonResponse(
                        {
                            "success": True,
                            "message": f"Successfully sent {email_type} emails to {processed_count} judges!",
                        }
                    )
                return JsonResponse({"error": "No email tuples to send"}, status=400)
            return JsonResponse({"error": "No judges processed"}, status=400)

        except Exception as e:
            print(f"Error: {e!s}")
            return JsonResponse({"error": str(e)}, status=500)

    def build_judge_interest_email(self, judge_data):
        """Build interest email from judge data"""
        subject = (
            f"Would you like to judge {settings.EVENT_NAME} {settings.EVENT_YEAR}?"
        )
        context = {
            "name": judge_data.get("name", "Friend"),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
        }
        html_message = render_to_string(
            "judgesmentors/emails/judge_interest.html", context
        )
        text_message = strip_tags(html_message)

        return subject, text_message, html_message, None, [judge_data.get("email")]

    def build_judge_confirmation_email(self, judge_data):
        """Build confirmation email with QR code from judge data"""

        user, _created = User.objects.get_or_create(
            email=judge_data["email"], defaults={"is_active": True}
        )

        _judge, _created = Judge.objects.get_or_create(
            user=user,
            defaults={
                "name": judge_data["name"],
                "phone": judge_data.get("phone", ""),
                "tshirt_size": judge_data.get("tshirt_size", "M"),
                "is_faculty": judge_data.get("is_faculty", False),
                "track": judge_data.get("track", "SW"),
                "additional_info": judge_data.get("additional_info", ""),
                "status": STATUS_CONFIRMED,
            },
        )

        name_parts = judge_data["name"].split()
        first_name = name_parts[0] if name_parts else "Judge"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        qr_content = json.dumps(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": judge_data["email"],
                "role": "judge",
                "university": "TAMU" if judge_data.get("is_faculty") else "External",
            }
        )

        qr_code = pyqrcode.create(qr_content)
        qr_stream = BytesIO()
        qr_code.png(qr_stream, scale=5)

        subject = f"Thank you for signing up to judge {settings.EVENT_NAME} {settings.EVENT_YEAR}!"
        context = {
            "name": judge_data.get("name", "Judge"),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
            "tshirt_size": judge_data.get("tshirt_size", "M"),
        }
        html_message = render_to_string(
            "judgesmentors/emails/judge_welcome.html", context
        )
        text_message = strip_tags(html_message)

        # Return EmailMultiAlternatives object instead of tuple
        email = EmailMultiAlternatives(
            subject, text_message, None, [judge_data.get("email")]
        )
        email.attach_alternative(html_message, "text/html")
        email.attach("code.png", qr_stream.getvalue(), "image/png")

        return email

    def process_mentors_csv(self, request):  # noqa: PLR0911
        """Process mentors CSV and send emails - no database storage"""
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)

        csv_file = request.FILES.get("csv_file")
        email_type = request.POST.get("email_type", "interest")

        if not csv_file:
            return JsonResponse({"error": "No CSV file provided"}, status=400)

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            io_string.seek(0)
            io_string.getvalue()

            io_string.seek(0)
            reader = csv.DictReader(io_string)

            mentors_data = []
            processed_count = 0

            for row in reader:
                mentor_data = self.normalize_row(row)
                mentors_data.append(mentor_data)
                processed_count += 1
                print(
                    f"Added mentor to memory: {mentor_data['name']} ({mentor_data['email']})"
                )

            # Send emails
            if processed_count > 0:
                email_tuples = []

                for mentor_data in mentors_data:
                    if email_type == "interest":
                        email_tuple = self.build_mentor_interest_email(mentor_data)
                        email_tuples.append(email_tuple)
                    else:  # confirmation
                        email_obj = self.build_mentor_confirmation_email(mentor_data)
                        email_obj.send()

                if email_type == "interest" and email_tuples:
                    send_mass_html_mail(email_tuples)
                    return JsonResponse(
                        {
                            "success": True,
                            "message": f"Successfully sent {email_type} emails to {len(email_tuples)} mentors!",
                        }
                    )
                if email_type == "confirmation":
                    return JsonResponse(
                        {
                            "success": True,
                            "message": f"Successfully sent {email_type} emails to {processed_count} mentors!",
                        }
                    )
                return JsonResponse({"error": "No email tuples to send"}, status=400)
            return JsonResponse({"error": "No mentors processed"}, status=400)

        except Exception as e:
            print(f"Error: {e!s}")
            return JsonResponse({"error": str(e)}, status=500)

    def build_mentor_interest_email(self, mentor_data):
        """Build interest email from mentor data"""
        subject = (
            f"Would you like to mentor at {settings.EVENT_NAME} {settings.EVENT_YEAR}?"
        )
        context = {
            "name": mentor_data.get("name", "Friend"),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
        }
        html_message = render_to_string(
            "judgesmentors/emails/mentor_interest.html", context
        )
        text_message = strip_tags(html_message)

        return subject, text_message, html_message, None, [mentor_data.get("email")]

    def build_mentor_confirmation_email(self, mentor_data):
        """Build confirmation email with QR code from mentor data"""
        # Create or get User
        user, _created = User.objects.get_or_create(
            email=mentor_data["email"], defaults={"is_active": True}
        )

        # Create or update Mentor
        _mentor, _created = Mentor.objects.get_or_create(
            user=user,
            defaults={
                "name": mentor_data["name"],
                "phone": mentor_data.get("phone", ""),
                "tshirt_size": mentor_data.get("tshirt_size", "M"),
                "is_faculty": mentor_data.get("is_faculty", False),
                "track": mentor_data.get("track", "SW"),
                "additional_info": mentor_data.get("additional_info", ""),
                "status": STATUS_CONFIRMED,
            },
        )

        # Generate QR code (same format as applicants)
        name_parts = mentor_data["name"].split()
        first_name = name_parts[0] if name_parts else "Mentor"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        qr_content = json.dumps(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": mentor_data["email"],
                "role": "mentor",
                "university": "TAMU" if mentor_data.get("is_faculty") else "External",
            }
        )

        qr_code = pyqrcode.create(qr_content)
        qr_stream = BytesIO()
        qr_code.png(qr_stream, scale=5)

        # Build email with QR code attachment
        subject = f"Thank you for signing up to mentor at {settings.EVENT_NAME} {settings.EVENT_YEAR}!"
        context = {
            "name": mentor_data.get("name", "Mentor"),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
            "track": mentor_data.get("track", "SW"),
            "tshirt_size": mentor_data.get("tshirt_size", "M"),
        }
        html_message = render_to_string(
            "judgesmentors/emails/mentor_welcome.html", context
        )
        text_message = strip_tags(html_message)

        # Return EmailMultiAlternatives object instead of tuple
        email = EmailMultiAlternatives(
            subject, text_message, None, [mentor_data.get("email")]
        )
        email.attach_alternative(html_message, "text/html")
        email.attach("code.png", qr_stream.getvalue(), "image/png")

        return email


csv_email_admin = CSVEmailAdminView()
