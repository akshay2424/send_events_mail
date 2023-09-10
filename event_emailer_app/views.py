from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

from .models import Employee, EmailTemplate, EventLog
from .serializers import EmployeeSerializer, EmailTemplateSerializer, EventLogSerializer
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SendEventEmails(APIView):
    def get(self, request):
        today = datetime.date.today()

        # Send birthday and work anniversary emails
        result = self.send_event_emails(today)

        if result['partially']:
            return Response({"message": "Partially successful. " + result['message']}, status=status.HTTP_206_PARTIAL_CONTENT)
        elif result['success']:
            return Response({"message": result['message']}, status=status.HTTP_200_OK)
        else:
            return Response({"message": result['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_event_emails(self, today):
        birthday_employees = Employee.objects.filter(dob__month=today.month, dob__day=today.day)
        anniversary_employees = Employee.objects.filter(join_date__month=today.month, join_date__day=today.day)

        if birthday_employees.exists() or anniversary_employees.exists():
            success = False
            message = "Failed to send all events."
            failed_count = 0
            # Events found, send emails
            for employee in birthday_employees:
                email_result = self.send_email(employee, 'birthday', today)
                if email_result['success']:
                    success = True  # At least one email succeeded
                else:
                    failed_count += 1
                message = email_result['message']

            for employee in anniversary_employees:
                email_result = self.send_email(employee, 'work_anniversary', today)
                if email_result['success']:
                    success = True  # At least one email succeeded
                else:
                    failed_count += 1
                message = email_result['message']

            partially = success and failed_count > 0  # Partially successful if some emails succeeded and some failed

            return {'success': success, 'message': message, 'partially': partially}
        else:
            # If no events found, add an entry in EventLog
            self.add_event_log("No events", today, "No events found for today.")
            return {'success': True, 'message': "No events found for today.", 'partially': False}
        
    def add_event_log(self, event_type, today, status , recipient=None, error_msg=None):
        try:
            EventLog.objects.create(event_type=event_type, sent_at=today, status=status, recipient=recipient, error_message=error_msg)
        except Exception as e:
            # Handle any exceptions that occur while creating the log entry
            pass

    def get_email_template(self, event_type):
        try:
            return EmailTemplate.objects.get(event_type=event_type)
        except EmailTemplate.DoesNotExist:
            return None

    def send_email(self, employee, event_type, today):
        template = self.get_email_template(event_type)

        # Load the HTML content from the template file
        template_name = f'{event_type.lower()}_email_template.html'  # Corrected template path
        html_content = render_to_string(template_name, {'employee': employee, 'template': template})

        # Create an EmailMultiAlternatives object to send both HTML and plain text versions
        subject = template.subject
        text_content = strip_tags(html_content)  # Extract plain text from HTML

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [employee.email])
        msg.attach_alternative(html_content, "text/html")

        retries = settings.RETRY
        while retries > 0:
            try:
                server = smtplib.SMTP(settings.EMAIL_HOST)
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                message = msg.message().as_bytes()
                server.sendmail(settings.DEFAULT_FROM_EMAIL, [employee.email], message)
                server.quit()

                # Log the successful email sending
                self.add_event_log(event_type, today, "Sent Successfully." , recipient=employee.email, error_msg='')
                return {'success': True, 'message': 'Emails Sent Successfully.'}
                break  # Email sent successfully, exit loop
            except Exception as e:
                # Log the error and decrement the retry count
                print(f"Error sending email: {str(e)}")
                retries -= 1

        if retries == 0:
            # All retries failed, mark as error in EventLog
            error_msg = 'Failed to send email after 3 retries.'
            self.add_event_log(event_type, today, "Failed to sent." , recipient=employee.email, error_msg=error_msg)
            return {'success': False, 'message': error_msg}
        
class AllDataAPIView(APIView):
    def get(self, request):
        # Retrieve data from each model
        employees = Employee.objects.all()
        templates = EmailTemplate.objects.all()
        event_logs = EventLog.objects.all()

        # Serialize data
        employee_data = EmployeeSerializer(employees, many=True).data
        template_data = EmailTemplateSerializer(templates, many=True).data
        event_logs = EventLogSerializer(event_logs, many=True).data
        # Create a response dictionary with data from all models and templates
        response_data = {
            'employees': employee_data,
            'templates': template_data,
            'event_logs' : event_logs
        }

        return Response(response_data, status=status.HTTP_200_OK)