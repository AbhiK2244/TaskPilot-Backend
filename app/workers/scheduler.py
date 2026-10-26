import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.init_db import create_db_and_tables
from app.workers.reminder_jobs import sync_reminder_jobs


def main() -> None:
    if settings.auto_create_tables:
        create_db_and_tables()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        sync_reminder_jobs,
        trigger="interval",
        minutes=1,
        args=[scheduler],
        id="sync-reminder-settings",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    sync_reminder_jobs(scheduler)
    scheduler.start()
    print("TaskPilot reminder scheduler is running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        print("Reminder scheduler stopped.")


if __name__ == "__main__":
    main()
