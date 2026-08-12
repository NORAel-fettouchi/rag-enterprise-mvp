"""
Test de connectivité isolé pour Hugging Face Inference API.

Vérifie que le endpoint router.huggingface.co/hf-inference/models
est joignable et teste plusieurs modèles candidats pour trouver
ceux supportés par le provider hf-inference.

Usage:
    python test_hf_connectivity.py
"""

import sys
from pathlib import Path
import requests

# Ajouter le répertoire racine au chemin
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from app.config import settings

# Modèles candidats (petits, instruct, adaptés à un usage gratuit/faible ressources)
CANDIDATE_MODELS = [
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "microsoft/Phi-3-mini-4k-instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "Qwen/Qwen2.5-7B-Instruct",
    "google/gemma-2-2b-it",
    "mistralai/Mistral-7B-Instruct-v0.2",  # modèle actuel (devrait échouer)
]

BASE_URL = settings.HUGGINGFACE_INFERENCE_URL.rstrip("/")
API_KEY = settings.HUGGINGFACE_API_KEY

print("=" * 70)
print("TEST CONNECTIVITÉ HUGGING FACE INFERENCE API")
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

payload = {
    "inputs": "Quelle est la capitale de la France ?",
    "parameters": {
        "max_new_tokens": 20,
        "return_full_text": False,
    },
}

print("Test des modèles candidats...")
print("-" * 70)

results = []

for model in CANDIDATE_MODELS:
    url = f"{BASE_URL}/{model}"
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        status = resp.status_code
        if status == 200:
            try:
                data = resp.json()
                if isinstance(data, list) and data:
                    text = data[0].get("generated_text", "")[:80]
                elif isinstance(data, str):
                    text = data[:80]
                else:
                    text = str(data)[:80]
                print(f"✅ {model} -> 200 OK | {text!r}")
                results.append((model, True))
            except Exception:
                print(f"✅ {model} -> 200 OK (réponse non parsée)")
                results.append((model, True))
        elif status == 400:
            body = resp.text[:120]
            print(f"❌ {model} -> 400 | {body}")
            results.append((model, False))
        else:
            print(f"⚠️  {model} -> {status} | {resp.text[:120]}")
            results.append((model, False))
    except requests.exceptions.Timeout:
        print(f"⏱️  {model} -> TIMEOUT (60s)")
        results.append((model, False))
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 {model} -> CONNECTION ERROR: {e}")
        results.append((model, False))
    except Exception as e:
        print(f"❌ {model} -> ERREUR: {e}")
        results.append((model, False))

print("-" * 70)
print()
print("RÉSUMÉ:")
working = [m for m, ok in results if ok]
if working:
    print(f"✅ Modèles supportés par le provider hf-inference:")
    for m in working:
        print(f"   - {m}")
else:
    print("❌ Aucun modèle testé n'est supporté par le provider hf-inference.")
    print("   Vérifiez la clé API et l'endpoint.")