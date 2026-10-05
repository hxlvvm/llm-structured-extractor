# LLM Structured Extractor

Turns free-text job ads into **validated JSON** with an LLM. The schema is a **Pydantic v2** model; its JSON schema
goes into the prompt, the reply is parsed and validated, and on failure the model is asked once more with the
validation error. Served through **FastAPI**.

## How it works
1. `extractor/schemas.py`: the `JobPosting` model (enums, ranges, email validation, skill de-duplication).
2. `extractor/llm.py`: prompt with the JSON schema, tolerant parsing (strips code fences), validate, retry with the
   error message, then fail clearly.
3. `extractor/api.py`: `POST /extract {"text": "..."}` returns the validated record (HTTP 422 if it cannot validate).

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # add GROQ_API_KEY (free at console.groq.com)
uvicorn extractor.api:app --reload
```

## Test (offline)
```bash
pytest -q
```
Tests use a scripted fake chat model, so they need no API key.

## Next steps
- Native structured output / tool calling instead of prompt-based JSON
- Batch extraction with asyncio
- An evaluation set with field-level accuracy
