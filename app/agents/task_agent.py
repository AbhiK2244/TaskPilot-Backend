from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

from app.agents.prompts import build_system_prompt
from app.agents.tools.task_tools import task_tools
from app.core.config import settings

_checkpointer = InMemorySaver()


def run_task_agent(message: str, thread_id: str) -> str:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env. Add your Groq API key to use the AI assistant.")

    model = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0,
    )
    agent = create_agent(
        model=model,
        tools=task_tools,
        system_prompt=build_system_prompt(),
        checkpointer=_checkpointer,
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        ).strip()
    return str(content)
