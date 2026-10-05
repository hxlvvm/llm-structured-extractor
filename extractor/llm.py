"""Turn text into a validated JobPosting with an LLM, retrying once with the validation error if the JSON is bad."""
import json

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from .schemas import JobPosting

SYSTEM = (
    "Extract the job posting into JSON that matches this JSON schema exactly. Use null when a field is not "
    "stated; never invent values. Reply with the JSON object only.\n\nSchema:\n{schema}"
)


def _parse(raw: str) -> JobPosting:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`").split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
    return JobPosting.model_validate(json.loads(text))


def extract(text: str, llm: BaseChatModel, max_retries: int = 1) -> JobPosting:
    messages = [SystemMessage(SYSTEM.format(schema=json.dumps(JobPosting.model_json_schema()))), HumanMessage(text)]
    for attempt in range(max_retries + 1):
        raw = llm.invoke(messages).content
        try:
            return _parse(raw)
        except (json.JSONDecodeError, ValidationError) as e:
            if attempt == max_retries:
                raise ValueError(f"model output did not validate: {e}") from e
            messages += [HumanMessage(f"Your previous reply was invalid: {e}. Reply with corrected JSON only.")]


def default_llm() -> BaseChatModel:
    from langchain_groq import ChatGroq  # needs GROQ_API_KEY

    return ChatGroq(model="llama-3.1-8b-instant", temperature=0)
