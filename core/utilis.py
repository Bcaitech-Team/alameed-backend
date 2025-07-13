# utils.py - Create a new file for your utility functions
import threading

from django.conf import settings
from django.template.loader import render_to_string

from core.gmail import send_gmail


class EmailThread(threading.Thread):
    """
    Thread class for sending emails asynchronously
    """

    def __init__(self, subject, html_content, from_email, recipient_list, attachment_files=None):
        self.subject = subject
        self.html_content = html_content
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.attachment_files = attachment_files or []
        threading.Thread.__init__(self)

    def run(self):
        for recipient in self.recipient_list:
            try:
                send_gmail(
                    to_email=recipient,
                    subject=self.subject,
                    message_html=self.html_content,
                    file_paths=self.attachment_files
                )
            except Exception as e:
                print(f"Error sending email to {recipient}: {e}")


def send_notification_email(subject, template_name, context, recipient_list, attachment_files=None, ):
    """
    Generic function to send notification emails using threads

    Args:
        instance: The model instance that triggered the notification
        subject: Email subject
        template_name: HTML template file name
        context: Context dictionary for the template
        attachment_files: List of file paths to attach to the email
    """
    # Admin email from settings
    admin_email = settings.EMAIL_HOST_USER

    # Render HTML email
    html_content = render_to_string(template_name, context)

    # Create and start email thread
    email_thread = EmailThread(
        subject=subject,
        html_content=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        attachment_files=attachment_files
    )
    email_thread.start()

    return True
