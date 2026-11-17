import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "contacts.json"


def load_contacts():
    if not MEMORY_FILE.exists():
        return {}

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_contacts(contacts):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4)


def remember_contact(name, email):
    contacts = load_contacts()

    contacts[name.strip().lower()] = email.strip()

    save_contacts(contacts)


def get_contact(name):
    contacts = load_contacts()

    return contacts.get(name.strip().lower())

def get_all_contacts():
    return load_contacts()