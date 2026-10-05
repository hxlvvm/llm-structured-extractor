from functools import lru_cache

from fastapi import FastAPI, HTTPException

from .llm import default_llm, extract
from .schemas import ExtractRequest, JobPosting

app = FastAPI(title="LLM Structured Extractor")


@lru_cache
def _llm():
    return default_llm()


def get_llm():
    return _llm()


@app.post("/extract", response_model=JobPosting)
def extract_posting(req: ExtractRequest) -> JobPosting:
    try:
        return extract(req.text, get_llm())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
