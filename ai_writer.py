import os, json
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
                "content": """You are a professional email assistant. 
                Return ONLY a valid JSON object. 
                The JSON must contain exactly these keys:
                'to', 'subject', 'body'. 
                Extract the recipient email address from the user's request. 
                Do not include markdown. 
                Do not include explanations. 
                Do not include any text outside the JSON."""
            },
            {
                "role": "user",
                "content": user_request
            }
        ],
        max_tokens=300
    )
    email_data = json.loads(
    response.choices[0].message.content
)
    return email_data   