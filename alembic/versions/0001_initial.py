"""Create TaskPilot tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_status", "task", ["status"], unique=False)
    op.create_index("ix_task_priority", "task", ["priority"], unique=False)
    op.create_index("ix_task_due_at", "task", ["due_at"], unique=False)

    op.create_table(
        "reminderpreference",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("reminder_times", sa.JSON(), nullable=False),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reminderlog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("occurrence_key", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminderlog_scheduled_for", "reminderlog", ["scheduled_for"], unique=False)
    op.create_index("ix_reminderlog_occurrence_key", "reminderlog", ["occurrence_key"], unique=True)

    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("thread_id", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_thread_id", "conversation", ["thread_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_conversation_thread_id", table_name="conversation")
    op.drop_table("conversation")
    op.drop_index("ix_reminderlog_occurrence_key", table_name="reminderlog")
    op.drop_index("ix_reminderlog_scheduled_for", table_name="reminderlog")
    op.drop_table("reminderlog")
    op.drop_table("reminderpreference")
    op.drop_index("ix_task_due_at", table_name="task")
    op.drop_index("ix_task_priority", table_name="task")
    op.drop_index("ix_task_status", table_name="task")
    op.drop_table("task")
