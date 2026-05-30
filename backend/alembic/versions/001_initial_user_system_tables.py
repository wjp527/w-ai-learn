"""initial user system tables

Revision ID: 001
Revises:
Create Date: 2026-05-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("openid", sa.String(length=64), nullable=False),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("openid", name="uk_users_openid"),
    )

    op.create_table(
        "question_sets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("knowledge_points", sa.JSON(), nullable=False),
        sa.Column("questions", sa.JSON(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_question_sets_user_created",
        "question_sets",
        ["user_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "study_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("question_set_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("accuracy", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("wrong_questions", sa.JSON(), nullable=False),
        sa.Column("weak_points", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["question_set_id"], ["question_sets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", name="uk_study_records_session_id"),
    )
    op.create_index(
        "idx_study_records_user_finished",
        "study_records",
        ["user_id", "finished_at"],
        unique=False,
    )
    op.create_index(
        "idx_study_records_question_set",
        "study_records",
        ["question_set_id", "finished_at"],
        unique=False,
    )

    op.create_table(
        "study_sessions_meta",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("question_set_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("answered_count", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["question_set_id"], ["question_sets.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_sessions_meta_user_status",
        "study_sessions_meta",
        ["user_id", "status", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_sessions_meta_user_status", table_name="study_sessions_meta")
    op.drop_table("study_sessions_meta")

    op.drop_index("idx_study_records_question_set", table_name="study_records")
    op.drop_index("idx_study_records_user_finished", table_name="study_records")
    op.drop_table("study_records")

    op.drop_index("idx_question_sets_user_created", table_name="question_sets")
    op.drop_table("question_sets")

    op.drop_table("users")
