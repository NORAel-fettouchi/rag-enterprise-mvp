from app.config import settings
from app.rag_pipeline_fixed import RAGPipeline

if not settings.HUGGINGFACE_API_KEY or 'METTEZ' in (settings.HUGGINGFACE_API_KEY or ''):
    print('HUGGINGFACE_API_KEY not set or placeholder; skipping live Hugging Face API test')
else:
    pipeline = RAGPipeline(reload_index=False)
    try:
        resp = pipeline._call_huggingface('Bonjour, test RAG réussi.')
        print('HF LIVE OK:')
        print(resp[:1000])
    except Exception as e:
        print('HF LIVE FAILED:')
        print(e)
