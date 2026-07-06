from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# This will be created automatically after login in next step
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

def send_email(to, subject, message):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("gmail", "v1", credentials=creds)

    email_message = {
        "raw": create_message(to, subject, message)
    }

    sent = service.users().messages().send(
        userId="me",
        body=email_message
    ).execute()

    print("Email sent! Message ID:", sent["id"])


def create_message(to, subject, message):
    import base64
    from email.mime.text import MIMEText

    msg = MIMEText(message)
    msg["to"] = to
    msg["subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return raw