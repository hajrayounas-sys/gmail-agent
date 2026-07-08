# Gmail Agent

An AI-powered Gmail assistant that converts natural language instructions into professional emails, requests user approval, and sends the email through the Gmail API.

## Version

Current Version: V2

## Features

- Natural language email drafting powered by the Hugging Face Inference API
- Contact memory for frequently used recipients
- Automatic retrieval of saved contacts from local memory
- Recipient extraction using Python regular expressions
- Structured email generation with `subject` and `body` fields
- Human-in-the-loop approval before sending emails
- Email delivery through the Gmail API using OAuth 2.0 authentication

### Supported Commands

- `Email my professor that I am sick.`
- `Email Alice inviting her to a party.`
- `Email professor@uni.edu about the assignment.`

## Version

Current Version: V1

This repository contains the first version of the Gmail Agent project. Future versions will introduce additional agent capabilities, improved reliability, and expanded email workflows.

## Project Structure

```text
gmail-agent/
│
├── .env.example          # Environment variable template
├── .gitignore            # Ignored files and secrets
├── ai_writer.py          # AI email drafting module
├── gmail_agent.py        # Main agent workflow
├── send_email.py         # Gmail sending functionality
├── setup_gmail_auth.py   # OAuth authentication setup
├── memory.py             # read, write, load contacts
├── contacts.json         # stores contacts as json object
├── requirements.txt
└── README.md
```

## How It Works

```text
User Instruction
        ↓
Recipient Resolution
(Email Address → Memory Lookup → User Prompt)
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

Input:

Email my professor that I was sick and will submit the assignment tomorrow.

Memory:

```json
{
  "professor": "professor@university.edu"
}
```

Generated Draft:

```text
To: professor@university.edu

Subject: Assignment Submission Update

Dear Professor,

I hope you are doing well. I was unwell and was unable to complete the assignment on time. I will submit the assignment tomorrow and appreciate your understanding.

Kind regards,
[Your Name]
```

The recipient is resolved through memory or user input, the AI generates the email content, and the user reviews the draft before deciding whether to send it.

## Requirements

- Python 3.12+
- Gmail API enabled in Google Cloud
- OAuth 2.0 credentials
- Hugging Face API token

## Setup

1. Install dependencies

```
pip install -r requirements.txt
```

2. Create a `.env` file

```
HF_TOKEN=your_huggingface_token
```

3. Configure Gmail OAuth credentials and place `credentials.json` in the project folder.

4. Run Gmail authentication:

```
python setup_gmail_auth.py
```

5. Run the agent:

```
python gmail_agent.py
```

## Technologies

- Python
- Gmail API
- OAuth 2.0
- Hugging Face Inference API (Llama 3.1 8B Instruct)
- Large Language Models (LLMs)

## Future Enhancements

- Support AI-assisted recipient extraction.
- Email summarization
- Reply drafting
- Multi-step agent workflows
- Inbox management capabilities

## Security

Do not commit the following files to GitHub:

- `.env`
- `credentials.json`
- `token.json`

These files contain API keys and authentication credentials and should remain private.

## Author

Hajra Younas
