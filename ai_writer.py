import os
import json

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)


def draft_email(user_request):

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {
                "role": "system",
                "content": """
You are a professional email assistant.

Generate an email based on the user's request.

Return ONLY a valid JSON object in exactly this format:

{
    "subject": "email subject",
    "body": "email body"
}

Rules:
- Use exactly two keys: "subject" and "body".
- Use double quotes around all JSON keys and string values.
- Do not use Markdown.
- Do not add ```json or ``` around the response.
- Do not include explanations.
- Do not include any text before or after the JSON.
"""
            },
            {
                "role": "user",
                "content": user_request
            }
        ],
        max_tokens=300
    )

    raw_response = response.choices[0].message.content.strip()

    print("\nDEBUG - AI response:")
    print(raw_response)
    print()

    # Remove Markdown code fences if the model still adds them
    if raw_response.startswith("```"):
        raw_response = raw_response.replace("```json", "")
        raw_response = raw_response.replace("```", "")
        raw_response = raw_response.strip()

    try:
        email_data = json.loads(raw_response)

    except json.JSONDecodeError:
        print("The AI did not return valid JSON.")
        print("Raw response was:")
        print(raw_response)
        raise

    # Make sure the expected fields exist
    if "subject" not in email_data or "body" not in email_data:
        raise ValueError(
            "AI response is missing 'subject' or 'body'."
        )

    return email_data