from ai_writer import draft_email
from send_email import send_email
from memory import remember_contact, get_contact, get_all_contacts
from contact_store import resolve_contact_from_sentence
import re

while True:
    request = input("What email would you like me to write and to whom?\n"
).strip()

    if request:
        break
    print("Please enter a request.")

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
contact_name = None

# First, check whether the user's request mentions a saved contact
contacts = get_all_contacts()

request_lower = request.lower()
request_words = re.findall(r"[a-zA-Z']+", request_lower)
cleaned_words = [w[:-2] if w.endswith("'s") else w for w in request_words]

for name in contacts:
    if name in cleaned_words:
        contact_name = name
        recipient_email = contacts[name]
        print(f"(Resolved '{contact_name}' via exact match)")
        break

if contact_name is None:
    match = resolve_contact_from_sentence(request)

    if match is not None:
        contact_name = match["name"]
        recipient_email = match["email"]
        print(f"(Resolved '{contact_name}' via semantic search, distance: {match['distance']:.4f})")
        
saved_email = None
#searching the address in the user prompt

email_match = re.search(
    r"[\w\.-]+@[\w\.-]+\.\w+",
    request
)

if email_match:
    recipient_email = email_match.group()

#memory lookup.
if contact_name:
    saved_email = get_contact(
        contact_name
    ) 
    if recipient_email is None:
        recipient_email = saved_email

#ask the user to provide the address.   
if recipient_email is None:
    if contact_name is None:
        contact_name = input(
            f"Please provide the contact's name: "
        ).strip()
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
# asking the user if user to update the existing address with the new address provided in user request
if (
    contact_name
    and saved_email
    and recipient_email
    and saved_email != recipient_email
):
    print(
        f"\nSaved email for '{contact_name}': "
        f"{saved_email}"
    )
    print(
        f"Current email used: "
        f"{recipient_email}"
    )
    update_choice = input(
        "Would you like to update the saved contact? (Y/N): "
    ).strip().lower()

    if update_choice == "y":
        remember_contact(
            contact_name,
            recipient_email
        )
        print(
            f"{contact_name} updated successfully."
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