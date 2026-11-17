import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = PROJECT_ROOT / "token.json"

def create_gmail_draft(
    to,
    subject,
    body,
    thread_id=None,
    in_reply_to=None,
    references=None
):
    # Prevent accidentally creating an unrelated draft
    # when we intend to reply to an existing conversation.
    if thread_id and not in_reply_to:
        raise ValueError(
            "The original Message-ID is required for a reply draft."
        )

    if not to or not subject or not body.strip():
        raise ValueError(
            "Recipient, subject, and body must not be empty."
        )

    # Load Gmail authorization

    creds = Credentials.from_authorized_user_file(
        str(TOKEN_FILE),
        ["https://www.googleapis.com/auth/gmail.modify"]
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    # Build the email message
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject

    if in_reply_to:
        message["In-Reply-To"] = in_reply_to

        reference_ids = (references or "").split()

        if in_reply_to not in reference_ids:
            reference_ids.append(in_reply_to)

        message["References"] = " ".join(reference_ids)

    message.set_content(body)

    # Encode the message for Gmail
    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    gmail_message = {"raw": encoded_message}

    if thread_id:
        gmail_message["threadId"] = thread_id

    # Create a draft, never send it
    draft = service.users().drafts().create(
        userId="me",
        body={"message": gmail_message}
    ).execute()

    print("Gmail draft created successfully!")
    print("Draft ID:", draft["id"])
    print("Thread ID:", thread_id or "Standalone draft")
    print("The email has NOT been sent.")

    return draft