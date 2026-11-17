# Gmail Agent

An AI-powered Gmail assistant built with Python and the Gmail API. The project contains two independent workflows:

1. **Interactive Email Assistant:** Converts natural language instructions into professional emails, resolves recipients using saved contacts and semantic search, requests user approval, and sends emails through Gmail.
2. **Inbox Reply Agent:** Monitors the Gmail inbox for unread incoming emails, generates replies using an LLM, and saves them as drafts in the original email threads for manual review.

Both workflows use the Gmail API, while the inbox-reply workflow uses Gemini for reply generation.

---

## Project Status

The project currently supports two working workflows:

- Interactive email drafting and sending with contact memory and semantic contact resolution.
- Automated inbox monitoring and AI-generated reply drafts.

The inbox-reply workflow has been tested with real incoming emails. It successfully detected an unread email present before startup and another email received while the agent was running. Both replies were saved as Gmail drafts.

**Important:** The inbox agent does not automatically send replies. All generated replies remain drafts until the user reviews and sends them.

Personalization using previously received and sent emails is a planned enhancement and has not yet been implemented.

---

## Interactive Email Assistant — V3

### What's New in V3

V2 relied on exact string matching for saved contacts, with an LLM-based fallback (`extract_recipient`) for anything else. That fallback could hallucinate a recipient name even when the user's request mentioned no one at all (e.g. *"Write an email apologizing for being late"*).

V3 introduced a **local RAG (Retrieval-Augmented Generation) pipeline**: contact names are embedded into vectors using a sentence-transformer model and stored in a local Chroma vector database. When a request doesn't exactly match a saved contact, the agent semantically searches this database instead of asking an LLM to guess.

This means recipient resolution is grounded in saved contacts rather than generated recipient guesses.

### Before / After

| Input | V2 (exact match + LLM guess) | V3 (RAG semantic search) |
|---|---|---|
| `"email my professor"` | Resolved through exact match | Resolved through exact match |
| `"email my supervisor"` (no exact contact named "supervisor") | Failed or LLM guessed a name | Resolved to a semantically similar saved contact |
| `"write an email to my mentor about rescheduling"` | Failed or LLM guessed a name | Resolved through semantic search |
| `"write an email apologizing for being late"` (no recipient) | LLM sometimes hallucinated a name | Correctly returns no match and asks the user |

### Features

- Natural language email drafting using the Hugging Face Inference API.
- Semantic contact resolution using a local RAG pipeline (Sentence-Transformers + ChromaDB).
- Whole-word exact contact matching.
- Contact memory for frequently used recipients, with manual save/update prompts.
- Structured email generation with `subject` and `body` fields.
- Human-in-the-loop approval before sending.
- Email delivery through the Gmail API using OAuth 2.0 authentication.

### Supported Commands

- `Email my professor that I am sick.`
- `Email Alice inviting her to a party.`
- `Email professor@uni.edu about the assignment.`
- `Write an email to my supervisor apologizing for being late.`

### How It Works

```text
User Instruction
       |
       v
Recipient Resolution
  1. Exact whole-word match against saved contacts
  2. Semantic search over contact embeddings
  3. If no confident match, ask the user
       |
       v
AI Email Drafting
       |
       v
Structured Output
(subject, body)
       |
       v
User Approval
       |
       v
Gmail API
       |
       v
Email Sent
```

---

## Inbox Reply Agent

The Inbox Reply Agent is a separate workflow that monitors the user's Gmail inbox and generates reply drafts for incoming unread emails.

Unlike the interactive assistant, it does not wait for a natural language instruction from the user. It periodically checks the inbox and processes newly detected unread messages.

### Features

- Periodic inbox monitoring using the Gmail API.
- Checks for unread incoming emails every 60 seconds.
- Detects unread emails present when the agent starts and newly received unread emails while it is running.
- Uses Gemini to generate structured replies containing a subject and body.
- Creates reply drafts in the original Gmail conversation thread.
- Maintains processing state in a local SQLite database to track processed messages.
- Avoids automatically sending generated replies.
- Includes retry handling for certain temporary API errors during reply generation.

### How It Works

```text
Gmail Inbox
     |
     v
Fetch Unread Emails
     |
     v
Check Processing State
     |
     v
Identify New Emails
     |
     v
Extract Email Content
     |
     v
Gemini Reply Generation
     |
     v
Validate Generated Reply
     |
     v
Create Gmail Draft
(in the original email thread)
     |
     v
Update Processing State
     |
     v
Continue Monitoring Inbox
```

### Reply Generation

The agent uses the incoming email's subject and body, along with sender information, to generate an appropriate reply.

The generated response is validated before being passed to the Gmail draft-creation module.

The reply is saved in the original conversation thread using Gmail message and thread references. This preserves the connection between the incoming email and its generated reply.

### Safety

The Inbox Reply Agent follows a draft-only approach:

- It creates Gmail drafts rather than sending replies automatically.
- The user can review and edit each generated reply.
- The user makes the final decision to send or discard a draft.

### Current Limitation

At present, the agent generates replies using the incoming email's content and the LLM's instructions. It does not yet retrieve relevant historical emails or previous replies to personalize the generated response.

---

## Planned Enhancement: Personalization Layer

The next planned development stage is to introduce a personalization layer into the Inbox Reply Agent.

The intended approach is to retrieve relevant historical emails and their corresponding replies to provide communication context for generating more personalized responses.

The proposed direction includes:

- Building a dataset from previously received emails and their replies.
- Generating embeddings for relevant email content.
- Retrieving semantically similar historical examples for a new incoming email.
- Using retrieved examples as contextual information during reply generation.
- Investigating retrieval relevance, confidence, and uncertainty to reduce the influence of unrelated or misleading examples.

The goal is to make generated replies more consistent with the user's communication style and previous interactions.

**Status:** Planned — not yet implemented.

---

## Project Structure

```text
gmail-agent/
│
├── interactive_assistant/
│   ├── gmail_agent.py
│   ├── contact_store.py
│   ├── memory.py
│   ├── recipient_extractor.py
│   ├── contacts.json
│   └── chroma_db/              # Generated locally
│
├── inbox_reply_agent/
│   ├── run_agent.py
│   ├── fetch_inbox.py
│   └── create_gmail_draft.py
│
├── ai_writer.py                # Shared AI generation functions
├── send_email.py               # Gmail email-sending functionality
├── setup_gmail_auth.py         # Gmail OAuth authentication
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Local Files (Not Committed)

The following files and directories are generated or maintained locally:

```text
gmail-agent/
│
├── .env
├── credentials.json
├── token.json
├── agent_state.db
└── .venv/
```

The `chroma_db/` directory is also generated locally when the contact vector database is initialized.

These files are excluded from version control.

---

## Technologies

| Technology | Purpose |
|---|---|
| Python 3.12+ | Core development language |
| Gmail API | Inbox access, email sending, and draft creation |
| OAuth 2.0 | Gmail authentication |
| Hugging Face Inference API | Email generation for the interactive assistant |
| Gemini API | AI reply generation for the Inbox Reply Agent |
| Sentence-Transformers (`all-MiniLM-L6-v2`) | Local contact embeddings |
| ChromaDB | Local vector database for semantic contact search |
| SQLite | Local processing-state management |
| JSON | Structured email responses and contact storage |
| Large Language Models (LLMs) | Email drafting and reply generation |

---

## Requirements

- Python 3.12 or later.
- A Google account with Gmail enabled.
- Gmail API enabled in Google Cloud Console.
- OAuth 2.0 credentials for a Desktop application.
- Hugging Face API token for the interactive assistant.
- Gemini API key for the Inbox Reply Agent.

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/hajrayounas-sys/gmail-agent.git
cd gmail-agent
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

```env
HF_TOKEN=your_huggingface_token
GEMINI_API_KEY=your_gemini_api_key
```

Provide the API credentials required by the workflows you intend to use.

### 5. Configure Gmail OAuth Credentials

1. Open Google Cloud Console.
2. Create or select a Google Cloud project.
3. Enable the Gmail API.
4. Configure the OAuth consent screen.
5. Create OAuth 2.0 credentials for a Desktop application.
6. Download the credentials file and save it as `credentials.json` in the project root.

### 6. Authenticate with Gmail

Run the authentication script from the project root:

```bash
python setup_gmail_auth.py
```

Complete the Google authorization flow in the browser.

The script generates `token.json`, which is used by the Gmail API modules.

The project uses the Gmail `gmail.modify` OAuth scope to support inbox access and draft creation, as well as the required email operations.

---

## Running the Project

Run either workflow independently from the project root.

### Option 1: Interactive Email Assistant

```bash
python interactive_assistant/gmail_agent.py
```

The assistant accepts natural language email instructions, resolves recipients using saved contacts, generates email content, requests user approval, and sends the approved email.

### Option 2: Inbox Reply Agent

```bash
python inbox_reply_agent/run_agent.py
```

The agent starts monitoring the inbox and checks for unread emails every 60 seconds.

When it detects a new email to process, it generates a reply and saves it as a draft in the original conversation.

Press `Ctrl+C` to stop the agent.

**Note:** The Inbox Reply Agent creates drafts only. It does not automatically send emails.

---

## Contact Vector Database

The Interactive Email Assistant uses ChromaDB to store and search contact embeddings.

The vector database is generated locally and excluded from Git.

If the contact index needs to be initialized or rebuilt, run:

```bash
python interactive_assistant/contact_store.py
```

This is relevant to the interactive assistant's contact-resolution workflow, not the Inbox Reply Agent's planned historical-email retrieval layer.

---

## Known Limitations

### Interactive Email Assistant

- **Small dataset:** The semantic contact search has been tested on a limited contact dataset. Its confidence threshold would need further validation with larger datasets.
- **No alias support:** A contact is primarily resolved through its saved key or semantically similar wording.
- **Multiple names in one request:** Requests containing multiple name-like entities may require additional disambiguation logic.
- **LLM output handling:** Malformed or unexpected model output can still require additional error handling.

### Inbox Reply Agent

- **No historical personalization:** Previous emails and replies are not yet retrieved to guide reply generation.
- **No automatic sending:** Replies remain drafts and require manual review and sending.
- **Polling-based monitoring:** The inbox is checked periodically rather than through real-time push notifications.
- **Local processing state:** Message-processing information is maintained in a local SQLite database and is not synchronized across machines.
- **Duplicate/crash recovery:** More robust recovery and idempotency handling could be added for situations where draft creation succeeds but processing-state updates do not complete.

---

## Future Enhancements

- Multiple aliases per contact.
- Improved recipient disambiguation.
- More robust LLM output validation and retry mechanisms.
- Retrieval of relevant historical email threads and replies.
- Personalized reply generation based on previous communication.
- Retrieval relevance and confidence estimation.
- Uncertainty-aware handling when retrieved examples are insufficient or irrelevant.
- Improved reliability and recovery for inbox processing.
- More advanced multi-step agent workflows.
- Expanded Gmail inbox management capabilities.

---

## Security

Never commit the following files or directories to GitHub:

- `.env` — contains API keys.
- `credentials.json` — contains Google OAuth client credentials.
- `token.json` — contains user authorization tokens.
- `.venv/` — local Python environment.
- `chroma_db/` — locally generated vector database.
- `agent_state.db` — local agent processing state.

These files are private, machine-specific, or regenerable and are excluded through `.gitignore`.

---

## Author

**Hajra Younas**

GitHub: [hajrayounas-sys](https://github.com/hajrayounas-sys)
