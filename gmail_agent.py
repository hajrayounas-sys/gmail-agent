from ai_writer import draft_email
from send_email import send_email
from memory import remember_contact, get_contact
import re

request = input(
    "What email would you like me to write and to whom?\n"
)
#for extracting email address from the user prompt.
match = re.search(
    r"remember that my (.+) is ([\w\.-]+@[\w\.-]+\.\w+)",
    request,
    re.IGNORECASE
)
if match:
    contact_name = match.group(1).strip()
    email = match.group(2).strip()

    remember_contact(contact_name, email)

    print(
        f"Remembered {contact_name}: {email}"
    )

    exit()
    
recipient_email = None
#searching the address in the user prompt

email_match = re.search(
    r"[\w\.-]+@[\w\.-]+\.\w+",
    request
)

if email_match:
    recipient_email = email_match.group()

#memory lookup.
if recipient_email is None:

    contact_match = re.search(
        r"email my (\w+)",
        request,
        re.IGNORECASE
    )

    if contact_match:
        contact_name = contact_match.group(1)

        recipient_email = get_contact(contact_name)

#ask the user to provide the address.   
if recipient_email is None:

    contact_match = re.search(
        r"email(?: my)? (\w+)",
        request,
        re.IGNORECASE
    )

    if contact_match:
        contact_name = contact_match.group(1)

        recipient_email = input(
            f"Please provide {contact_name}'s email address: "
        ).strip()

        remember_choice = input(
            f"Would you like me to remember {contact_name} for future emails? (Y/N): "
        ).strip().lower()

        if remember_choice == "y":
            remember_contact(
                contact_name,
                recipient_email
            )

email_data = draft_email(request)

print("\n" + "=" * 50)
print("EMAIL DRAFT")
print("=" * 50)

print(f"To: {recipient_email}")
print(f"Subject: {email_data['subject']}")
print("\nBody:\n")
print(email_data['body'])

print("\n" + "=" * 50)

approval = input(
    "\nSend this email? (Y/N): "
).strip().lower()

if approval == "y":
    send_email(
        to=recipient_email,
        subject=email_data["subject"],
        message=email_data["body"]
    )
    print("Email sent successfully!")
else:
    print("Email cancelled.")