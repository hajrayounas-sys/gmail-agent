import sqlite3
import time
import sys
from pathlib import Path
from email.utils import parseaddr

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_inbox import fetch_inbox
from ai_writer import draft_reply
from create_gmail_draft import create_gmail_draft

POLL_INTERVAL = 60
DATABASE_FILE = str(PROJECT_ROOT / "agent_state.db")

def setup_database():
    """Create the local database if it does not already exist."""
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS email_status (
                message_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS agent_settings (
                setting TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

def get_status(message_id):
    with sqlite3.connect(DATABASE_FILE) as connection:
        result = connection.execute(
            "SELECT status FROM email_status WHERE message_id = ?",
            (message_id,)
        ).fetchone()

    return result[0] if result else None

def set_status(message_id, status):
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("""
            INSERT INTO email_status (message_id, status)
            VALUES (?, ?)
            ON CONFLICT(message_id) DO UPDATE SET
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
        """, (message_id, status))

def establish_initial_baseline(emails):
    """
    On the first run only, record existing inbox emails so they
    are not mistaken for newly arrived messages.
    """
    with sqlite3.connect(DATABASE_FILE) as connection:
        result = connection.execute(
            "SELECT value FROM agent_settings WHERE setting = ?",
            ("baseline_complete",)
        ).fetchone()

        if result:
            return False

        for email in emails:
            connection.execute("""
                INSERT OR IGNORE INTO email_status (message_id, status)
                VALUES (?, ?)
            """, (email["id"], "baseline"))

        connection.execute("""
            INSERT INTO agent_settings (setting, value)
            VALUES (?, ?)
        """, ("baseline_complete", "true"))

    print(
        f"Initial baseline saved for {len(emails)} existing emails."
    )
    return True


def process_email(email):
    """Generate a reply draft for one new email."""

    if not email["body"].strip():
        print("Skipped: email has no readable body.")
        return False

    if not email["thread_id"] or not email["message_id"]:
        print("Skipped: missing thread or message information.")
        return False

    sender_address = parseaddr(email["from"])[1]

    if not sender_address:
        print("Skipped: could not identify sender's email address.")
        return False

    print("\nGenerating a reply...")
    print("Subject:", email["subject"])
    print("From:", email["from"])

    reply = draft_reply(
        incoming_subject=email["subject"],
        incoming_body=email["body"],
        sender=email["from"]
    )

    if not reply["subject"].strip() or not reply["body"].strip():
        raise ValueError("The generated reply is empty.")

    create_gmail_draft(
        to=sender_address,
        subject=reply["subject"],
        body=reply["body"],
        thread_id=email["thread_id"],
        in_reply_to=email["message_id"],
        references=email["references"]
    )

    return True


def run_agent():
    setup_database()

    print("Starting Gmail Agent...")
    print(f"Checking the inbox every {POLL_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.\n")

    # Fetch existing messages and establish a baseline only once.
    initial_emails = fetch_inbox(unread_only=True)
    establish_initial_baseline(initial_emails)

    # Warn about work interrupted by a previous shutdown.
    with sqlite3.connect(DATABASE_FILE) as connection:
        interrupted = connection.execute("""
            SELECT COUNT(*) FROM email_status
            WHERE status = 'processing'
        """).fetchone()[0]

    if interrupted:
        print(
            f"Warning: {interrupted} email(s) have an unfinished "
            "processing record. They will not be retried automatically "
            "to avoid creating duplicate drafts."
        )

    print("Agent is ready.")

    while True:
        try:
            time.sleep(POLL_INTERVAL)
            print("\nChecking for new emails...")

            emails = fetch_inbox(unread_only=True)

            for email in reversed(emails):
                message_id = email["id"]
                status = get_status(message_id)

                # Skip messages already handled or being processed.
                if status in (
                    "baseline",
                    "completed",
                    "processing",
                    "skipped",
                    "failed"
                ):
                    continue

                # Record the attempt BEFORE generating or creating
                # a draft, so a restart won't blindly repeat it.
                set_status(message_id, "processing")

                try:
                    success = process_email(email)

                    if success:
                        set_status(message_id, "completed")
                        print("Email processed successfully.")
                    else:
                        set_status(message_id, "skipped")

                except Exception as error:
                    set_status(message_id, "failed")
                    print("Could not process this email.")
                    print(type(error).__name__ + ":", error)
                    print("No email was sent.")

        except KeyboardInterrupt:
            print("\nGmail Agent stopped.")
            break

        except Exception as error:
            print("Inbox check failed.")
            print(type(error).__name__ + ":", error)
            print("The agent will try again at the next check.")


if __name__ == "__main__":
    run_agent()
