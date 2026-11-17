import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = PROJECT_ROOT / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def decode_body(data):
    """Decode an email body from Gmail's Base64 URL-safe format."""
    if not data:
        return ""

    data += "=" * (-len(data) % 4)
    decoded = base64.urlsafe_b64decode(data)
    return decoded.decode("utf-8", errors="replace")

def extract_body(payload):
    """Extract the plain-text body from an email payload."""
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        return decode_body(body_data)

    for part in payload.get("parts", []):
        body = extract_body(part)
        if body:
            return body

    return ""

def fetch_inbox(unread_only=False):

    creds = Credentials.from_authorized_user_file(
        str(TOKEN_FILE),
        SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    request_args = {
    "userId": "me",
    "labelIds": ["INBOX"],
    "maxResults": 50
    }

    if unread_only:
        request_args["q"] = "is:unread"

    results = service.users().messages().list(
         **request_args
).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No inbox messages found.")
        return []

    emails = []

    for message in messages:
        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        headers = email.get("payload", {}).get("headers", [])
        details = {
            header["name"].lower(): header["value"]
            for header in headers
        }

        email_data = {
            "id": email["id"],
            "thread_id": email.get("threadId"),
            "from": details.get("from", "Unknown"),
            "subject": details.get("subject", "(No subject)"),
            "date": details.get("date", "Unknown"),
            "message_id": details.get("message-id", ""),
            "references": details.get("references", ""),
            "body": extract_body(email.get("payload", {}))
        }

        emails.append(email_data)

        print("Message ID:", email_data["id"])
        print("From:", email_data["from"])
        print("Subject:", email_data["subject"])
        print("Date:", email_data["date"])
        print("Body preview:", email_data["body"][:300])
        print("-" * 40)

    return emails


if __name__ == "__main__":
    fetch_inbox()
