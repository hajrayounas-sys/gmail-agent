# Gmail Agent

An AI-powered Gmail assistant that converts natural language instructions into professional emails, requests user approval, and sends the email through the Gmail API.

## Features

* Natural language email drafting using Hugging Face Inference API
* Extraction of recipient details from natural language instructions
* Structured email generation (`to`, `subject`, `body`)
* Human-in-the-loop approval before sending
* Email delivery through the Gmail API using OAuth 2.0 authentication

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
├── requirements.txt
└── README.md
```

## How It Works

```text
User Instruction
        ↓
AI Email Drafting
        ↓
Structured Output
(to, subject, body)
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

Generated Output:

```
{
  "to": "professor@example.com",
  "subject": "Assignment Submission Update",
  "body": "..."
}
```

The user reviews the draft and decides whether to send it.

## Requirements

* Python 3.12+
* Gmail API enabled in Google Cloud
* OAuth 2.0 credentials
* Hugging Face API token

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

* Python
* Gmail API
* OAuth 2.0
* Hugging Face Inference API (Llama 3.1 8B Instruct)
* Large Language Models (LLMs)

## Future Enhancements

* Contact memory and retrieval
* Email summarization
* Reply drafting
* Multi-step agent workflows
* Inbox management capabilities

## Security

Do not commit the following files to GitHub:

* `.env`
* `credentials.json`
* `token.json`

These files contain API keys and authentication credentials and should remain private.

## Author

Hajra Younas
