import base64
import mimetypes
import os
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_credentials(credentials_path, token_path):
    """
    Gets valid user credentials for Gmail API.

    Args:
        credentials_path: Path to credentials.json file
        token_path: Path to token.json file

    Returns:
        Credentials, the obtained credential.
    """
    creds = None

    # Check if token file exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If credentials don't exist or are invalid, go through the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def create_message(sender, to, subject, message_text=None, message_html=None):
    """
    Creates a message for an email without attachments.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        message_html: The HTML content of the email message.

    Returns:
        A dict containing a base64url encoded email object.
    """
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Add plain text part if provided
    if message_text:
        message.attach(MIMEText(message_text, 'plain'))

    # Add HTML part if provided
    if message_html:
        message.attach(MIMEText(message_html, 'html'))

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}


def create_message_with_attachment(sender, to, subject, message_text=None,
                                   message_html=None, file_paths=None):
    """
    Creates a message for an email with attachments.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        message_html: The HTML content of the email message.
        file_paths: List of file paths to be attached.

    Returns:
        A dict containing a base64url encoded email object.
    """
    # Start with a mixed container
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Create a multipart/alternative child container for text and HTML parts
    msg_alternative = MIMEMultipart('alternative')

    # Add plain text part if provided
    if message_text:
        msg_alternative.attach(MIMEText(message_text, 'plain'))

    # Add HTML part if provided
    if message_html:
        msg_alternative.attach(MIMEText(message_html, 'html'))

    # Attach the alternative part to the main message
    message.attach(msg_alternative)

    # Add attachments if provided
    if file_paths:
        for file_path in file_paths:
            # Skip if file doesn't exist
            if not os.path.exists(file_path):
                print(f"Warning: File not found - {file_path}")
                continue

            # Get file MIME type
            content_type, encoding = mimetypes.guess_type(file_path)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            main_type, sub_type = content_type.split('/', 1)

            try:
                with open(file_path, 'rb') as file:
                    file_data = file.read()

                    if main_type == 'text':
                        attachment = MIMEText(file_data.decode('utf-8'), _subtype=sub_type)
                    elif main_type == 'image':
                        attachment = MIMEImage(file_data, _subtype=sub_type)
                    elif main_type == 'audio':
                        attachment = MIMEAudio(file_data, _subtype=sub_type)
                    else:
                        attachment = MIMEBase(main_type, sub_type)
                        attachment.set_payload(file_data)
                        encoders.encode_base64(attachment)

                    # Add filename to the attachment
                    file_name = os.path.basename(file_path)
                    attachment.add_header('Content-Disposition', 'attachment', filename=file_name)

                    # Attach to the message
                    message.attach(attachment)
                    print(f"Successfully attached: {file_name}")
            except Exception as e:
                print(f"Error attaching file {file_path}: {e}")

    # Encode the complete message
    try:
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    except Exception as e:
        print(f"Error encoding message: {e}")
        return None


def send_message(credentials, sender, to, subject, message_text=None, message_html=None, file_paths=None):
    """
    Sends an email message via Gmail API.

    Args:
        credentials: Valid credentials for Gmail API.
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        message_html: The HTML content of the email message.
        file_paths: List of file paths to be attached.

    Returns:
        Sent Message.
    """
    try:
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        # Create appropriate message
        if file_paths:
            message = create_message_with_attachment(
                sender, to, subject, message_text, message_html, file_paths
            )
        else:
            message = create_message(sender, to, subject, message_text, message_html)

        if not message:
            return None

        # Send the message
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        return sent_message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def send_gmail(to_email, subject, message_text=None, message_html=None, file_paths=None):
    """
    Sends an email using Gmail API.

    Args:
        to_email: Email address of the recipient.
        subject: Email subject.
        message_text: Plain text message content (optional).
        message_html: HTML message content (optional).
        file_paths: List of file paths to be attached (optional).

    Returns:
        Dictionary with success status and message or error details.
    """
    try:
        # Get paths for credentials and token
        print("BASE_DIR", settings.BASE_DIR)
        credentials_path = settings.BASE_DIR / 'secrets/credentials.json'
        token_path = settings.BASE_DIR / 'secrets/token.json'

        # Ensure credentials file exists
        if not os.path.exists(credentials_path):
            return {
                'success': False,
                'error': f"Credentials file not found at {credentials_path}"
            }

        # Get credentials
        credentials = get_credentials(credentials_path, token_path)

        # Get sender email from settings
        sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if not sender_email:
            return {
                'success': False,
                'error': "DEFAULT_FROM_EMAIL not defined in settings"
            }

        # Send the message
        result = send_message(
            credentials=credentials,
            sender=sender_email,
            to=to_email,
            subject=subject,
            message_text=message_text,
            message_html=message_html,
            file_paths=file_paths
        )

        if result:
            return {
                'success': True,
                'message_id': result.get('id', 'Unknown'),
                'message': f"Email sent successfully to {to_email}"
            }
        else:
            return {
                'success': False,
                'error': "Failed to send email"
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
