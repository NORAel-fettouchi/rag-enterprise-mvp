"""
Test isolé du endpoint OpenAI-compatible de Hugging Face Inference API.

Vérifie que https://router.huggingface.co/v1/chat/completions
fonctionne avec un modèle supporté.

Usage:
    python test_hf_chat.py
"""

import sys
import json
from pathlib import Path
import requests

# Ajouter le répertoire racine au chemin
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from app.config import settings

API_KEY = settings.HUGGINGFACE_API_KEY
BASE_URL = "https://router.huggingface.co/v1/chat/completions"

print("=" * 70)
print("TEST CHAT COMPLETIONS HUGGING FACE INFERENCE API")
print("=" * 70)
print(f"Endpoint: {BASE_URL}")
print(f"Clé API configurée: {'OUI' if API_KEY else 'NON'}")
print()

if not API_KEY:
    print("❌ HUGGINGFACE_API_KEY manquante dans .env")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Modèles candidats (petits, instruct, adaptés à un usage gratuit/faible ressources)
CANDIDATE_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen3-4B-Instruct-2507",
    "google/gemma-3-4b-it",
    "microsoft/phi-4",
    "meta-llama/Llama-3.1-8B-Instruct",
]

payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {"role": "user", "content": "Quelle est la capitale de la France ? Réponds en une phrase."}
    ],
    "max_tokens": 50,
    "temperature": 0.1,
}

print("Test du endpoint chat/completions avec Qwen/Qwen2.5-7B-Instruct...")
print("-" * 70)

try:
    resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text[:500]}")
    print()
    
    if resp.status_code == 200:
        data = resp.json()
        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"]["content"]
            print(f"✅ SUCCÈS! Réponse: {content!r}")
        else:
            print(f"⚠️  Réponse 200 mais format inattendu: {data}")
    else:
        print(f"❌ Échec: {resp.text[:300]}")
except requests.exceptions.Timeout:
    print("⏱️  TIMEOUT (60s)")
except requests.exceptions.ConnectionError as e:
    print(f"🔌 CONNECTION ERROR: {e}")
except Exception as e:
    print(f"❌ ERREUR: {e}")