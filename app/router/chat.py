from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import get_or_create_conversation
from app.agents.task_agent import run_task_agent

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat_with_taskpilot(payload: ChatRequest, session: Session = Depends(get_session)):
    get_or_create_conversation(session, payload.thread_id)
    try:
        answer = run_task_agent(payload.message, payload.thread_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The AI assistant could not complete this request. Check the Groq API key/model and try again.",
        )
    return ChatResponse(thread_id=payload.thread_id, response=answer)
