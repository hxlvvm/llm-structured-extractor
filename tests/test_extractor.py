import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from extractor import api
from extractor.llm import extract

AD = "Acme is hiring a junior Python Developer in Karachi. 1 year experience with FastAPI required; LangChain preferred."
GOOD = ('{"title": "Python Developer", "company": "Acme", "location": "Karachi", "remote": false, '
        '"seniority": "junior", "min_years_experience": 1, "required_skills": ["Python", "FastAPI", "python"], '
        '"preferred_skills": ["LangChain"]}')


def test_extract_valid_json_and_dedups_skills():
    out = extract(AD, FakeListChatModel(responses=[GOOD]))
    assert out.title == "Python Developer" and out.seniority == "junior"
    assert out.required_skills == ["Python", "FastAPI"]


def test_retry_after_invalid_output():
    out = extract(AD, FakeListChatModel(responses=["not json", "```json\n" + GOOD + "\n```"]))
    assert out.company == "Acme"


def test_gives_up_after_retries():
    with pytest.raises(ValueError):
        extract(AD, FakeListChatModel(responses=["oops", '{"title": 5, "min_years_experience": -3}']))


def test_api_endpoint(monkeypatch):
    monkeypatch.setattr(api, "get_llm", lambda: FakeListChatModel(responses=[GOOD]))
    client = TestClient(api.app)
    r = client.post("/extract", json={"text": AD})
    assert r.status_code == 200 and r.json()["location"] == "Karachi"
    assert client.post("/extract", json={"text": "too short"}).status_code == 422
