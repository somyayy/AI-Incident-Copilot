"""
LLM client responsible for generating root cause analysis, resolution
suggestions, and postmortem summaries using retrieved incident context.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
    return _llm


RCA_SYSTEM_PROMPT = """You are an expert Site Reliability Engineer assistant.
Given an incident description, its logs, and a set of similar historical
incidents, produce:
1. A concise Root Cause Analysis (RCA).
2. A step-by-step suggested resolution.

Be specific, technical, and reference the historical incidents when relevant.
Format your answer as:

ROOT CAUSE ANALYSIS:
<analysis>

SUGGESTED RESOLUTION:
<steps>
"""

POSTMORTEM_SYSTEM_PROMPT = """You are an SRE assistant writing a blameless
postmortem summary. Given the incident details, its root cause analysis, and
resolution steps taken, write a concise postmortem covering: Summary,
Impact, Root Cause, Resolution, and Follow-up Action Items."""


def _format_similar_incidents(similar_incidents: list[dict]) -> str:
    if not similar_incidents:
        return "No similar historical incidents found."
    lines = []
    for i, inc in enumerate(similar_incidents, start=1):
        lines.append(f"{i}. {inc.get('title', 'Untitled')}: {inc.get('text', '')[:300]}")
    return "\n".join(lines)


def generate_rca_and_resolution(
    title: str,
    description: str,
    logs: str | None,
    similar_incidents: list[dict],
) -> dict:
    """Call the LLM to produce an RCA + resolution, grounded on retrieved context."""
    llm = get_llm()

    user_prompt = f"""Incident Title: {title}

Description:
{description}

Logs:
{logs or "No logs provided."}

Similar Historical Incidents:
{_format_similar_incidents(similar_incidents)}
"""

    messages = [
        SystemMessage(content=RCA_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    content = response.content

    rca, resolution = _split_rca_response(content)
    return {"root_cause_analysis": rca, "suggested_resolution": resolution}


def _split_rca_response(content: str) -> tuple[str, str]:
    """Best-effort split of the model's formatted response into two sections."""
    rca_marker = "ROOT CAUSE ANALYSIS:"
    resolution_marker = "SUGGESTED RESOLUTION:"

    rca_part, resolution_part = content, ""
    if rca_marker in content and resolution_marker in content:
        rca_part = content.split(rca_marker, 1)[1].split(resolution_marker, 1)[0].strip()
        resolution_part = content.split(resolution_marker, 1)[1].strip()

    return rca_part, resolution_part


def generate_postmortem(
    title: str,
    description: str,
    root_cause_analysis: str,
    suggested_resolution: str,
) -> str:
    llm = get_llm()

    user_prompt = f"""Incident Title: {title}

Description:
{description}

Root Cause Analysis:
{root_cause_analysis}

Resolution Taken:
{suggested_resolution}
"""

    messages = [
        SystemMessage(content=POSTMORTEM_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return response.content
