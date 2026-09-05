import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)


def extract_recipient(user_request):

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {
                "role": "system",
                "content": """You extract the recipient from email requests.
Return ONLY the recipient name.

Examples:

Input:
Email my professor that I am sick.

Output:
professor

Input:
I need to email my professor and ask if he could review my project report.

Output:
professor

Input:
Write an email to Alice inviting her to dinner.

Output:
Alice

Input:
Send an email to Bob about tomorrow's meeting.

Output:
Bob

Input:
Email Dr. Ahmed about my research proposal.

Output:
Dr. Ahmed

Do not explain.
Do not write sentences.
Return only the recipient name."""
            },
            {
                "role": "user",
                "content": user_request
            }
        ],
        max_tokens=20
    )

    return response.choices[0].message.content.strip()