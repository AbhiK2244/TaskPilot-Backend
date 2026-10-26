from sqlmodel import Session, select
from datetime import datetime, timezone

from app.core.dates import utc_now_naive
from app.models.conversation import Conversation


def get_or_create_conversation(session: Session, thread_id: str) -> Conversation:
    conversation = session.exec(select(Conversation).where(Conversation.thread_id == thread_id)).first()
    if conversation:
        return conversation

    conversation = Conversation(thread_id=thread_id, created_at=datetime.now(timezone.utc))
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
