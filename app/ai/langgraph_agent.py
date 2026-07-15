"""
LangGraph Agent for Pharmaceutical CRM Interaction Extraction.

This module implements a StateGraph workflow:
START -> receive_message -> build_prompt -> call_llm -> 
validate_extraction -> (if complete) generate_record | (if incomplete) ask_question -> END
"""

import json
import re
from typing import TypedDict, Annotated, List, Optional
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START

from app.core.config import settings
from app.ai.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class CRMState(TypedDict):
    """State that flows through the LangGraph nodes."""
    messages: Annotated[List[dict], "Conversation history"]
    user_message: str
    ai_response: str
    extracted_data: Optional[dict]
    is_complete: bool
    missing_fields: List[str]


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def get_llm(model: str = "llama-3.3-70b-versatile") -> ChatGroq:
    """Return a configured Groq LLM instance."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=model,
        temperature=0.3,
        max_tokens=1024,
    )


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = ["doctor_name", "hospital", "products_discussed", "summary", "sentiment"]


def _parse_json_from_response(text: str) -> Optional[dict]:
    """Attempt to parse a JSON block from an LLM response."""
    # Try to find EXTRACTION_COMPLETE marker
    if "EXTRACTION_COMPLETE:" in text:
        json_part = text.split("EXTRACTION_COMPLETE:", 1)[1].strip()
        try:
            return json.loads(json_part)
        except Exception:
            pass

    # Try to find raw JSON block
    json_match = re.search(r"\{[\s\S]+\}", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except Exception:
            pass
    return None


def _check_missing_fields(data: dict) -> List[str]:
    """Return a list of required fields that are empty / None / missing."""
    missing = []
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if not value or (isinstance(value, list) and len(value) == 0):
            missing.append(field)
    return missing


# ---------------------------------------------------------------------------
# LangGraph nodes
# ---------------------------------------------------------------------------

def receive_message(state: CRMState) -> CRMState:
    """Append the new user message to conversation history."""
    state["messages"].append({"role": "user", "content": state["user_message"]})
    state["is_complete"] = False
    state["extracted_data"] = None
    return state


def build_and_call_llm(state: CRMState) -> CRMState:
    """Build prompt and call Groq LLM."""
    llm = get_llm()

    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in state["messages"]:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_messages.append(AIMessage(content=msg["content"]))

    response = llm.invoke(langchain_messages)
    ai_text = response.content

    state["ai_response"] = ai_text
    state["messages"].append({"role": "assistant", "content": ai_text})
    return state


def validate_extraction(state: CRMState) -> CRMState:
    """Try to extract JSON from the AI response and validate required fields."""
    ai_text = state["ai_response"]
    extracted = _parse_json_from_response(ai_text)

    if extracted:
        missing = _check_missing_fields(extracted)
        state["extracted_data"] = extracted
        state["missing_fields"] = missing
        state["is_complete"] = len(missing) == 0
    else:
        state["extracted_data"] = None
        state["missing_fields"] = REQUIRED_FIELDS
        state["is_complete"] = False

    return state


def generate_final_record(state: CRMState) -> CRMState:
    """Finalise extracted data — add timestamp if visit_date is missing."""
    if state["extracted_data"] and not state["extracted_data"].get("visit_date"):
        state["extracted_data"]["visit_date"] = datetime.now().strftime("%Y-%m-%d")
    return state


def route_after_validation(state: CRMState) -> str:
    """Conditional edge: go to final_record if complete, else stay (end turn)."""
    return "generate_final_record" if state["is_complete"] else END


# ---------------------------------------------------------------------------
# Build the StateGraph
# ---------------------------------------------------------------------------

def build_crm_graph() -> StateGraph:
    graph = StateGraph(CRMState)

    graph.add_node("receive_message", receive_message)
    graph.add_node("build_and_call_llm", build_and_call_llm)
    graph.add_node("validate_extraction", validate_extraction)
    graph.add_node("generate_final_record", generate_final_record)

    graph.add_edge(START, "receive_message")
    graph.add_edge("receive_message", "build_and_call_llm")
    graph.add_edge("build_and_call_llm", "validate_extraction")
    graph.add_conditional_edges(
        "validate_extraction",
        route_after_validation,
        {
            "generate_final_record": "generate_final_record",
            END: END,
        },
    )
    graph.add_edge("generate_final_record", END)

    return graph.compile()


# Singleton compiled graph
crm_graph = build_crm_graph()


# ---------------------------------------------------------------------------
# Public API used by the router
# ---------------------------------------------------------------------------

async def process_chat_message(messages: List[dict], user_message: str) -> dict:
    """
    Process a single chat turn through the LangGraph workflow.

    Returns:
        {
            "response": str,          # AI reply to show the user
            "is_complete": bool,      # True when all required data extracted
            "extracted_data": dict | None
        }
    """
    initial_state: CRMState = {
        "messages": list(messages),
        "user_message": user_message,
        "ai_response": "",
        "extracted_data": None,
        "is_complete": False,
        "missing_fields": [],
    }

    result = await crm_graph.ainvoke(initial_state)

    # Strip the EXTRACTION_COMPLETE marker from the user-facing response
    ai_response = result["ai_response"]
    if "EXTRACTION_COMPLETE:" in ai_response:
        ai_response = (
            "✅ I've gathered all the information needed. "
            "Here is the extracted interaction record. Please review and save."
        )

    return {
        "response": ai_response,
        "is_complete": result["is_complete"],
        "extracted_data": result["extracted_data"],
        "messages": result["messages"],
    }


async def extract_from_conversation(messages: List[dict]) -> dict:
    """
    Force-extract structured data from an existing conversation using a dedicated extraction prompt.
    """
    llm = get_llm("llama-3.3-70b-versatile")

    conversation_text = "\n".join(
        f"{'Rep' if m['role'] == 'user' else 'AI'}: {m['content']}"
        for m in messages
    )

    prompt = EXTRACTION_PROMPT.format(conversation=conversation_text)
    response = llm.invoke([HumanMessage(content=prompt)])

    extracted = _parse_json_from_response(response.content)
    if not extracted:
        # Return raw text for debugging
        extracted = {"raw": response.content}

    return extracted
