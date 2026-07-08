import json

MEMORY_FILE = "contacts.json"

def load_contacts():
    with open(MEMORY_FILE, "r") as file:
        return json.load(file)
    
def save_contacts(contacts):
    with open(MEMORY_FILE, "w") as file:
        json.dump(contacts, file, indent=4)

def remember_contact(name, email):
    contacts = load_contacts()

    contacts[name.lower()] = email

    save_contacts(contacts)

def get_contact(name):
    contacts = load_contacts()

    return contacts.get(name.lower()) 