from time import sleep

from google.genai import errors

MAX_ATTEMPTS = 3
FALLBACK_MODELS = ("gemini-3.7-flash", "gemini-3.6-flash")

def generate_content_with_retry(client, **request):
    primary_model = request["model"]
    last_error = None
    models = (primary_model,) + tuple(model for model in FALLBACK_MODELS if model != primary_model)
    for model_index, model in enumerate(models):
        attempts = MAX_ATTEMPTS if model_index == 0 else 1
        for attempt in range(attempts):
            try:
                return client.models.generate_content(**{**request, "model": model})
            except errors.APIError as exc:
                if exc.code not in (429, 503):
                    raise
                last_error = exc
                if exc.code == 429:
                    break
                if attempt < attempts - 1:
                    sleep(2 ** attempt)

    raise last_error