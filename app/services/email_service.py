from pathlib import Path

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def send_daily_digest(email: str, timezone_name: str, overdue: list[dict], due_today: list[dict], upcoming: list[dict]):
    if not settings.resend_api_key:
        raise RuntimeError("RESEND_API_KEY is missing from .env")

    resend.api_key = settings.resend_api_key
    html = templates.get_template("daily_digest.html").render(
        timezone=timezone_name,
        overdue=overdue,
        due_today=due_today,
        upcoming=upcoming,
    )
    return resend.Emails.send(
        {
            "from": settings.resend_from_email,
            "to": [email],
            "subject": "TaskPilot task reminder",
            "html": html,
        }
    )
