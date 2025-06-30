from django.contrib import admin
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from shared.admin_functions import send_mass_html_mail
import csv
import io
import json


class CSVEmailAdminView:
    """Lightweight CSV to Email admin interface - no database storage"""
    
    def get_urls(self):
        from django.contrib.admin.views.decorators import staff_member_required
        return [
            path('judges/', staff_member_required(self.judge_email_view), name='csv_judge_emails'),
            path('mentors/', staff_member_required(self.mentor_email_view), name='csv_mentor_emails'),
            path('judges/process/', staff_member_required(self.process_judges_csv), name='process_judges_csv'),
            path('mentors/process/', staff_member_required(self.process_mentors_csv), name='process_mentors_csv'),
        ]
    
    def judge_email_view(self, request):
        """Display the judge CSV upload and email interface"""
        context = {
            'title': 'Judge CSV Email System',
            'type': 'judges',
            'opts': {'app_label': 'judgesmentors', 'model_name': 'judge'},
        }
        return render(request, 'admin/csv_email_interface.html', context)
    
    def mentor_email_view(self, request):
        """Display the mentor CSV upload and email interface"""
        context = {
            'title': 'Mentor CSV Email System', 
            'type': 'mentors',
            'opts': {'app_label': 'judgesmentors', 'model_name': 'mentor'},
        }
        return render(request, 'admin/csv_email_interface.html', context)
    
    def process_judges_csv(self, request):
        """Process judges CSV and send emails - no database storage"""
        if request.method != "POST":
            return JsonResponse({'error': 'POST required'}, status=405)
            
        csv_file = request.FILES.get("csv_file")
        email_type = request.POST.get('email_type', 'interest')
        
        if not csv_file:
            return JsonResponse({'error': 'No CSV file provided'}, status=400)
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
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
                print(f"Processing row: {row}")
                is_faculty = str(row.get('is_tamu_faculty', '')).lower() in ['yes', 'true', '1', 'y']
                
                judge_data = {
                    'name': row.get('name', '').strip(),
                    'email': row.get('email', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'tshirt_size': row.get('tshirt_size', 'M').upper(),
                    'is_tamu_faculty': is_faculty,
                    'track': row.get('track', 'SW').upper(),
                    'additional_info': row.get('additional_info', '').strip(),
                }
                
                judges_data.append(judge_data)
                processed_count += 1
                print(f"Added judge to memory: {judge_data['name']} ({judge_data['email']})")
            
            # Send emails
            if processed_count > 0:
                print(f"=== SENDING {email_type.upper()} EMAILS TO {processed_count} JUDGES ===")
                email_tuples = []
                
                for judge_data in judges_data:
                    print(f"Building {email_type} email for: {judge_data['name']} ({judge_data.get('email', 'unknown')})")
                    if email_type == 'interest':
                        email_tuple = self.build_judge_interest_email(judge_data)
                    else:  # confirmation
                        email_tuple = self.build_judge_confirmation_email(judge_data)
                    email_tuples.append(email_tuple)
                
                if email_tuples:
                    print(f"Sending {len(email_tuples)} {email_type} emails...")
                    send_mass_html_mail(email_tuples)
                    print("=== EMAILS SENT SUCCESSFULLY ===")
                    return JsonResponse({
                        'success': True, 
                        'message': f'Successfully sent {email_type} emails to {len(email_tuples)} judges!'
                    })
                else:
                    return JsonResponse({'error': 'No email tuples to send'}, status=400)
            else:
                return JsonResponse({'error': 'No judges processed'}, status=400)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def build_judge_interest_email(self, judge_data):
        """Build interest email from judge data"""
        subject = f"TEST: Would you like to judge {settings.EVENT_NAME} {settings.EVENT_YEAR}? (Original: {judge_data.get('name', 'Unknown')})"
        context = {
            "name": judge_data.get('name', 'Friend'),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
        }
        html_message = render_to_string("judgesmentors/emails/judge_interest.html", context)
        text_message = strip_tags(html_message)
        
        test_email = "ajmds66@gmail.com"
        print(f"TESTING: Redirecting interest email from {judge_data.get('email', 'unknown')} to {test_email}")
        return subject, text_message, html_message, None, [test_email]
    
    def build_judge_confirmation_email(self, judge_data):
        """Build confirmation email from judge data"""
        subject = f"TEST: Thank you for signing up to judge {settings.EVENT_NAME} {settings.EVENT_YEAR}! (Original: {judge_data.get('name', 'Unknown')})"
        context = {
            "name": judge_data.get('name', 'Judge'),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
            "tshirt_size": judge_data.get('tshirt_size', 'M'),
        }
        html_message = render_to_string("judgesmentors/emails/judge_welcome.html", context)
        text_message = strip_tags(html_message)
        
        test_email = "ajmds66@gmail.com"
        print(f"TESTING: Redirecting confirmation email from {judge_data.get('email', 'unknown')} to {test_email}")
        return subject, text_message, html_message, None, [test_email]
    
    def process_mentors_csv(self, request):
        """Process mentors CSV and send emails - no database storage"""
        if request.method != "POST":
            return JsonResponse({'error': 'POST required'}, status=405)
            
        csv_file = request.FILES.get("csv_file")
        email_type = request.POST.get('email_type', 'interest')
        
        if not csv_file:
            return JsonResponse({'error': 'No CSV file provided'}, status=400)
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            
            print("=== CSV UPLOAD - MENTORS ===")
            print(f"File: {csv_file.name}")
            print(f"Size: {csv_file.size} bytes")
            print(f"Email type: {email_type}")
            print("CSV Content:")
            
            io_string.seek(0)
            csv_content = io_string.getvalue()
            print(csv_content)
            print("=== END CSV CONTENT ===")
            
            io_string.seek(0)
            reader = csv.DictReader(io_string)
            
            mentors_data = []
            processed_count = 0
            
            for row in reader:
                print(f"Processing row: {row}")
                is_faculty = str(row.get('is_tamu_faculty', '')).lower() in ['yes', 'true', '1', 'y']
                
                mentor_data = {
                    'name': row.get('name', '').strip(),
                    'email': row.get('email', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'tshirt_size': row.get('tshirt_size', 'M').upper(),
                    'is_tamu_faculty': is_faculty,
                    'track': row.get('track', 'SW').upper(),
                    'additional_info': row.get('additional_info', '').strip(),
                }
                
                mentors_data.append(mentor_data)
                processed_count += 1
                print(f"Added mentor to memory: {mentor_data['name']} ({mentor_data['email']})")
            
            # Send emails
            if processed_count > 0:
                print(f"=== SENDING {email_type.upper()} EMAILS TO {processed_count} MENTORS ===")
                email_tuples = []
                
                for mentor_data in mentors_data:
                    print(f"Building {email_type} email for: {mentor_data['name']} ({mentor_data.get('email', 'unknown')})")
                    if email_type == 'interest':
                        email_tuple = self.build_mentor_interest_email(mentor_data)
                    else:  # confirmation
                        email_tuple = self.build_mentor_confirmation_email(mentor_data)
                    email_tuples.append(email_tuple)
                
                if email_tuples:
                    print(f"Sending {len(email_tuples)} {email_type} emails...")
                    send_mass_html_mail(email_tuples)
                    print("=== EMAILS SENT SUCCESSFULLY ===")
                    return JsonResponse({
                        'success': True, 
                        'message': f'Successfully sent {email_type} emails to {len(email_tuples)} mentors!'
                    })
                else:
                    return JsonResponse({'error': 'No email tuples to send'}, status=400)
            else:
                return JsonResponse({'error': 'No mentors processed'}, status=400)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def build_mentor_interest_email(self, mentor_data):
        """Build interest email from mentor data"""
        subject = f"TEST: Would you like to mentor at {settings.EVENT_NAME} {settings.EVENT_YEAR}? (Original: {mentor_data.get('name', 'Unknown')})"
        context = {
            "name": mentor_data.get('name', 'Friend'),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
        }
        html_message = render_to_string("judgesmentors/emails/mentor_interest.html", context)
        text_message = strip_tags(html_message)
        
        test_email = "ajmds66@gmail.com"
        print(f"TESTING: Redirecting mentor interest email from {mentor_data.get('email', 'unknown')} to {test_email}")
        return subject, text_message, html_message, None, [test_email]
    
    def build_mentor_confirmation_email(self, mentor_data):
        """Build confirmation email from mentor data"""
        subject = f"TEST: Thank you for signing up to mentor at {settings.EVENT_NAME} {settings.EVENT_YEAR}! (Original: {mentor_data.get('name', 'Unknown')})"
        context = {
            "name": mentor_data.get('name', 'Mentor'),
            "event_name": settings.EVENT_NAME,
            "organizer_name": settings.ORGANIZER_NAME,
            "event_year": settings.EVENT_YEAR,
            "organizer_email": settings.ORGANIZER_EMAIL,
            "event_date_text": settings.EVENT_DATE_TEXT,
            "track": mentor_data.get('track', 'SW'),
            "tshirt_size": mentor_data.get('tshirt_size', 'M'),
        }
        html_message = render_to_string("judgesmentors/emails/mentor_welcome.html", context)
        text_message = strip_tags(html_message)
        
        test_email = "ajmds66@gmail.com"
        print(f"TESTING: Redirecting mentor confirmation email from {mentor_data.get('email', 'unknown')} to {test_email}")
        return subject, text_message, html_message, None, [test_email]


csv_email_admin = CSVEmailAdminView()