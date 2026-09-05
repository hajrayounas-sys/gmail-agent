Absolutely, love. I’ll keep the **content and meaning the same**, but clean up the Markdown formatting, spacing, escaping, headings, tables, and code blocks so you can copy it directly into `README.md`.

````markdown
# Gmail Agent

An AI-powered Gmail assistant that converts natural language instructions into professional emails, resolves recipients using semantic search over saved contacts, requests user approval, and sends the email through the Gmail API.

## Version

Current Version: V3

## What's New in V3

V2 relied on exact string matching for saved contacts, with an LLM-based fallback (`extract_recipient`) for anything else. That fallback was found to hallucinate — inventing a recipient name even when the user's request mentioned no one at all (e.g. _"Write an email apologizing for being late"_).

V3 replaces that fallback with a **local RAG (Retrieval-Augmented Generation) pipeline**: contact names are embedded into vectors using a sentence-transformer model and stored in a local Chroma vector database. When a request doesn't exactly match a saved contact, the agent semantically searches this database instead of asking an LLM to guess — meaning it can only ever resolve to a contact that actually exists, never invent one.

### Before / After

| Input                                                               | V2 (exact match + LLM guess)         | V3 (RAG semantic search)                                     |
| ------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------ |
| `"email my professor"`                                              | ✅ Resolved (exact match)            | ✅ Resolved (exact match)                                    |
| `"email my supervisor"` (no exact contact named "supervisor")       | ❌ Failed or LLM guessed a name      | ✅ Resolved to `professor` (distance 0.91)                   |
| `"write an email to my mentor about rescheduling"`                  | ❌ Failed or LLM guessed a name      | ✅ Resolved to `professor` (distance 0.99)                   |
| `"write an email apologizing for being late"` (no recipient at all) | ⚠️ LLM sometimes hallucinated a name | ✅ Correctly returns no match, falls back to asking the user |

## Features

- Natural language email drafting powered by the Hugging Face Inference API
- **Semantic contact resolution using a local RAG pipeline** (sentence-transformers + Chroma)
- Whole-word exact contact matching (fixed from V2, which matched substrings — e.g. "friend" inside "friend's" or "boyfriend" could previously match incorrectly)
- Contact memory for frequently used recipients, with manual save/update prompts
- Structured email generation with `subject` and `body` fields
- Human-in-the-loop approval before sending emails
- Email delivery through the Gmail API using OAuth 2.0 authentication

### Supported Commands

- `Email my professor that I am sick.`
- `Email Alice inviting her to a party.`
- `Email professor@uni.edu about the assignment.`
- `Write an email to my supervisor apologizing for being late.` _(new: resolves via semantic search, no exact contact named "supervisor" needed)_

## Project Structure

```text
gmail-agent/
│
├── .env.example          # Environment variable template
├── .gitignore            # Ignored files and secrets
├── ai_writer.py          # AI email drafting module
├── gmail_agent.py        # Main agent workflow
├── contact_store.py      # RAG pipeline: embeds contacts, builds/searches vector index
├── send_email.py         # Gmail sending functionality
├── setup_gmail_auth.py   # OAuth authentication setup
├── memory.py             # read, write, load contacts
├── contacts.json         # stores contacts as json object
├── requirements.txt
└── README.md
```
````

**Note:** `chroma_db/` is generated automatically the first time `contact_store.py` runs, and is excluded from version control via `.gitignore`.

## How It Works

```text
User Instruction
        ↓
Recipient Resolution
  1. Exact whole-word match against saved contacts
  2. Semantic search (RAG) over contact embeddings — sliding-window
     search across the sentence, with a confidence threshold
  3. If no confident match → ask the user directly
        ↓
AI Email Drafting
        ↓
Structured Output
(subject, body)
        ↓
User Approval
        ↓
Gmail API
        ↓
Email Sent
```

## Example

### Input

Write an email to my mentor about rescheduling our meeting.

### Contacts (`contacts.json`)

```json
{
  "professor": "professor@university.edu"
}
```

### Resolution

No exact match for "mentor" → semantic search →

Resolved `professor` via semantic search (distance: 0.9959)

### Generated Draft

```text
To: professor@university.edu

Subject: Request to Reschedule Our Meeting

Hi Professor, I was wondering if we could reschedule our meeting...
```

The recipient is resolved through exact match, then semantic search, then user input as a last resort. The AI generates the email content, and the user reviews the draft before deciding whether to send it.

## Requirements

- Python 3.12+
- Gmail API enabled in Google Cloud
- OAuth 2.0 credentials
- Hugging Face API token

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
HF_TOKEN=your_huggingface_token
```

### 3. Configure Gmail OAuth credentials

Place `credentials.json` in the project folder.

### 4. Run Gmail authentication

```bash
python setup_gmail_auth.py
```

### 5. Build the contact vector index

This is required once, and again any time `contacts.json` is edited by hand:

```bash
python contact_store.py
```

### 6. Run the agent

```bash
python gmail_agent.py
```

## Technologies

- Python
- Gmail API
- OAuth 2.0
- Hugging Face Inference API (Llama 3.1 8B Instruct)
- Sentence-Transformers (`all-MiniLM-L6-v2`) — local embedding model
- ChromaDB — local vector database for semantic search
- Large Language Models (LLMs)

## Known Limitations

- **Small dataset:** currently tested against ~20 contacts; the confidence threshold (`max_distance`) was tuned on limited examples and would need re-validation at a larger scale.

- **No alias support yet:** a contact can only be found by the exact key stored in `contacts.json` or something semantically close to it.

- **Single-recipient sentences only:** if a sentence mentions more than one name-like word (e.g. "email Alice about our friend's wedding"), the current logic may resolve to the wrong one, since it isn't designed to disambiguate between multiple named entities in one request.

- **`ai_writer.py` JSON parsing is not fully fault-tolerant:** the LLM occasionally returns malformed JSON, which currently raises an error rather than retrying automatically.

## Future Enhancements

- Multiple aliases per contact (e.g. "sister", "Alice" → same email)
- Retry/self-correction when the LLM returns malformed JSON
- Disambiguation logic for sentences mentioning multiple names
- Retrieval-augmented draft generation: pulling relevant past email threads with a contact before drafting a follow-up, rather than relying on the prompt alone
- Reply drafting
- Multi-step agent workflows
- Inbox management capabilities

## Security

Do not commit the following files to GitHub:

- `.env`
- `credentials.json`
- `token.json`
- `chroma_db/`

These contain API keys, authentication credentials, or locally generated data, and should remain private/regenerable rather than versioned.

## Author

Hajra Younas

```
```
