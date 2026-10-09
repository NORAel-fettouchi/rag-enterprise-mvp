import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")

url = "https://router.huggingface.co/v1/chat/completions"

models = [
    "Qwen/Qwen3-8B",
    "meta-llama/Llama-3.1-8B-Instruct",
]

for model in models:
    print("\n" + "=" * 70)
    print("TEST :", model)
    print("=" * 70)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Réponds simplement : Bonjour, test RAG réussi."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 50,
    }

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )

        print("HTTP :", response.status_code)
        print("Réponse :")
        print(response.text)

    except Exception as e:
        print("ERREUR :", e)