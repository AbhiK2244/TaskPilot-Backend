# TaskPilot Backend

TaskPilot is a task management backend built with **FastAPI**. It includes an AI task assistant powered by Groq and LangGraph, scheduled email reminders, and productivity analytics.

All API routes are organized under `app/router/`.

## Features

- **Task Management:** Create, view, update, delete, filter, and paginate tasks.
- **AI Task Assistant:** Chat with an AI agent that can manage tasks using the same services as the REST API.
- **Conversation Memory:** Maintain conversations using a client-provided `thread_id` while the API process is running.
- **Email Reminders:** Send task reminders using Resend.
- **Scheduled Reminders:** Run reminders at configured times using a separate APScheduler process.
- **Reminder History:** View previous reminder attempts.
- **Productivity Analytics:** View task statistics, completion rates, and overdue tasks.
- **Database Migrations:** Manage database changes using Alembic.
- **Database Support:** Use PostgreSQL for persistent storage or SQLite for local development.

Authentication, RAG, embeddings, frontend, automated tests, Redis, Celery, and Docker are outside the current scope.

## Tech Stack

- **Backend:** FastAPI, Python
- **Database:** SQLite / PostgreSQL (choose one)
- **ORM:** SQLModel
- **AI:** Groq, LangChain, LangGraph
- **Email:** Resend
- **Scheduler:** APScheduler
- **Migrations:** Alembic (optional)

## 1. Installation

Open PowerShell in the project directory and run:

```powershell
py -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt 

copy .env.example .env
```

Update `.env` with your configuration. Never commit this file to Git.

## 2. Database Configuration

### Option A: PostgreSQL

Create a PostgreSQL database named `taskpilot` and update your `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/taskpilot
```

Replace `YOUR_PASSWORD` with your PostgreSQL password. URL-encode special characters in the password when necessary.

### Option B: SQLite

For a quick local setup without installing PostgreSQL, use:

```env
DATABASE_URL=sqlite:///./taskpilot.db
```

Set the following option to create tables automatically when the API starts:

```env
AUTO_CREATE_TABLES=true
```

SQLite is suitable for local learning and development. PostgreSQL is recommended for deployment.

## 3. Configure the AI Assistant

Create an API key through [GroqCloud](https://console.groq.com/) and add it to `.env`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Change `GROQ_MODEL` if you want to use another model available to your account.

Without a Groq API key, task management, reminders, and analytics can still work. The chat endpoint requires a valid key.

## 4. Configure Email Reminders

Create a Resend API key and add the following settings to `.env`:

```env
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=onboarding@resend.dev
REMINDER_EMAIL=your_test_recipient@example.com
TIMEZONE=Asia/Kolkata
```

Use a sender and recipient permitted by your Resend account.

Next, configure reminder preferences through the API.

**Endpoint:** `PUT /api/v1/reminders/settings`

Example request body:

```json
{
  "email": "you@example.com",
  "enabled": true,
  "reminder_times": ["12:00", "18:00", "23:00"],
  "timezone": "Asia/Kolkata"
}
```

The settings control the recipient, whether reminders are enabled, the reminder times, and the timezone.

The scheduler checks for updated reminder settings every minute, so changes do not require a restart.

## 5. Run the Backend

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Once the server starts, you can access:

- **API documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Root endpoint:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

The Swagger UI allows you to explore endpoints and send requests directly from your browser.

## 6. Run the Reminder Scheduler

The reminder scheduler runs separately from the API server.

Open a second PowerShell terminal in the project directory and activate the virtual environment:

```powershell
.venv\Scripts\activate
python -m app.workers.scheduler
```

Keep this process running to send scheduled reminders.

**Note:** Starting the FastAPI server alone does not start the scheduler.

## 7. Database Migrations

TaskPilot supports two ways to create database tables:

- Automatic table creation using `SQLModel.metadata.create_all()`.
- Database migrations using Alembic.

Choose one approach for a given database.

### Run the initial migration

For a fresh database managed by Alembic:

1. Set `AUTO_CREATE_TABLES=false` in `.env`.
2. Run the migration:

```powershell
alembic upgrade head
```

The initial migration, `0001_initial`, creates the required tables.

### Create a migration for model changes

After changing your database models, run:

```powershell
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Review autogenerated migration files before applying them.

**Important:** If automatic table creation has already created the tables, do not apply the initial migration to that same database. It may fail because the tables already exist.

## 8. API Endpoints

All endpoints use the `/api/v1` prefix.

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List tasks with optional filters and pagination |
| `GET` | `/tasks/{task_id}` | Get a task by ID |
| `PATCH` | `/tasks/{task_id}` | Update selected task fields |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

The task list supports these query parameters:

- `status`
- `priority`
- `limit`
- `offset`

### AI Assistant

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a message to the AI task assistant |

### Reminders

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/reminders/settings` | Get reminder settings |
| `PUT` | `/reminders/settings` | Update reminder settings |
| `GET` | `/reminders/history` | View reminder attempts |
| `POST` | `/reminders/trigger` | Trigger reminders manually |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/summary` | Get task totals and productivity statistics |
| `GET` | `/analytics/status-breakdown` | Get task counts grouped by status |
| `GET` | `/analytics/overdue` | List overdue tasks |

## 9. Example API Requests

You can try these examples through Swagger UI at `/docs` or using an API client.

### Create a Task

**Endpoint:** `POST /api/v1/tasks`

```json
{
  "title": "Finish FastAPI project",
  "description": "Complete TaskPilot API endpoints",
  "priority": "high",
  "due_at": "2026-11-01T18:00:00+05:30",
  "estimated_minutes": 120
}
```

Use ISO 8601 timestamps with an explicit timezone offset when needed. The application stores timestamps as UTC without timezone information.

### Filter Tasks

**Endpoint:** `GET /api/v1/tasks?status=pending&priority=high&limit=20&offset=0`

This retrieves pending, high-priority tasks with pagination.

### Update a Task

**Endpoint:** `PATCH /api/v1/tasks/1`

```json
{
  "status": "completed"
}
```

When a task is marked as completed, `completed_at` is set automatically. Reopening a completed task clears this timestamp.

### Chat with the AI Assistant

**Endpoint:** `POST /api/v1/chat`

```json
{
  "message": "List my high-priority tasks",
  "thread_id": "conversation-123"
}
```

Example response:

```json
{
  "thread_id": "conversation-123",
  "response": "Here are your high-priority tasks..."
}
```

Reuse the same `thread_id` to continue a conversation.

Conversation messages are stored in memory and are lost when the API process restarts. The database's `conversation` table stores metadata only; it does not persist the chat history.

### Get Productivity Analytics

**Endpoint:** `GET /api/v1/analytics/summary`

Example response:

```json
{
  "total_tasks": 8,
  "pending_tasks": 3,
  "in_progress_tasks": 2,
  "completed_tasks": 3,
  "overdue_tasks": 1,
  "tasks_due_today": 2,
  "completion_percentage": 37.5
}
```

These are example values. Actual results depend on the tasks stored in the database.

A task is considered overdue when its deadline has passed and it has not been completed.

## 10. How the AI Assistant Works

The AI assistant uses LangGraph to interact with tasks through predefined tools.

1. The `/api/v1/chat` endpoint receives a message and `thread_id`.
2. `app/agents/task_agent.py` creates the Groq chat model and LangGraph agent.
3. Tools in `app/agents/tools/task_tools.py` validate inputs and call the task service.
4. The task service uses the same repository as the REST API.
5. `InMemorySaver` maintains conversation state by `thread_id` while the process is running.
6. Deleting a task requires a confirmation step before the delete operation runs.

The AI assistant does not have unrestricted access to the database or direct SQL execution.

## 11. Verify the Backend

After configuring the database and environment variables, follow these steps:

1. Start the FastAPI server and open `/docs`.
2. Create a task using `POST /api/v1/tasks`.
3. Retrieve and update the task using the task endpoints.
4. Check the results through `/api/v1/analytics/summary`.
5. Configure reminder settings and verify your Resend email configuration.
6. Create an outstanding task and call `POST /api/v1/reminders/trigger`.
7. Check `GET /api/v1/reminders/history` for reminder attempts.
8. Configure `GROQ_API_KEY` and test `POST /api/v1/chat`.

### Reminder Notes

- Email delivery requires valid Resend credentials and an authorized sender.
- The reminder recipient must be configured.
- At least one outstanding task must exist for a useful reminder.
- The manual trigger can send reminders even when the scheduled reminders are disabled, but it still requires a valid recipient, outstanding tasks, and working email credentials.
- Scheduled reminder sends are deduplicated using an occurrence key to prevent duplicate sends for the same scheduled occurrence.

## 12. Future Scope of Improvements

TaskPilot can be extended with the following features in future updates:

- **Authentication:** Add user registration, login, and secure access to personal tasks.
- **Persistent Chat History:** Store conversation messages in the database so users can continue conversations after restarting the application.
- **Frontend Development:** Build a user-friendly interface to manage tasks, interact with the AI assistant, configure reminders, and view productivity analytics.
- **Advanced AI Features:** Add RAG and embeddings to provide more context-aware assistance.
- **Background Job Processing:** Use a dedicated worker service for reliable scheduling and email delivery in production.
- **Testing:** Add automated tests for API endpoints, task management, reminders, and AI tools.


These improvements can be implemented gradually as the project grows.


**Security note:** Do not expose this backend publicly with real user data until authentication and appropriate deployment protections have been implemented.