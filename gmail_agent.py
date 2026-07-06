from ai_writer import draft_email
from send_email import send_email

request = input(
    "What email would you like me to write and to whom?\n"
)

email_data = draft_email(request)

print("\n" + "=" * 50)
print("EMAIL DRAFT")
print("=" * 50)

print(f"To: {email_data['to']}")
print(f"Subject: {email_data['subject']}")
print("\nBody:\n")
print(email_data['body'])

print("\n" + "=" * 50)

approval = input(
    "\nSend this email? (Y/N): "
).strip().lower()

if approval == "y":
    send_email(
        to=email_data["to"],
        subject=email_data["subject"],
        message=email_data["body"]
    )
    print("Email sent successfully!")
else:
    print("Email cancelled.")
    
if __name__ == "__main__":
    main()    