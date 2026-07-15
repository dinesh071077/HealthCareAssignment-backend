from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.ai.langgraph_agent import process_chat_message, extract_from_conversation

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    user_message: str


class ExtractRequest(BaseModel):
    messages: List[Message]


@router.post("")
async def chat(request: ChatRequest):
    """Send a user message and receive an AI response via the LangGraph workflow."""
    history = [{"role": m.role, "content": m.content} for m in request.messages]
    result = await process_chat_message(history, request.user_message)
    return result


@router.post("/extract")
async def extract(request: ExtractRequest):
    """Force-extract structured CRM data from the current conversation."""
    history = [{"role": m.role, "content": m.content} for m in request.messages]
    extracted = await extract_from_conversation(history)
    return {"extracted_data": extracted}
