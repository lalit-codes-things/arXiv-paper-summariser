"""v3 research platform

Revision ID: 0001_v3
Revises:
Create Date: 2026-05-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_v3"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "papers",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("arxiv_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("authors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("topics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("contributions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("paper_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("arxiv_id"),
    )
    op.create_index("ix_papers_arxiv_id", "papers", ["arxiv_id"])
    op.create_index("ix_papers_created_at", "papers", ["created_at"])
    op.create_index("ix_papers_title", "papers", ["title"])
    op.create_index("ix_papers_topics_gin", "papers", ["topics"], postgresql_using="gin")
    op.create_index("ix_papers_contributions_gin", "papers", ["contributions"], postgresql_using="gin")
    op.execute(
        "CREATE INDEX ix_papers_search_vector "
        "ON papers USING gin "
        "(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(abstract, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(methodology, '')))"
    )

    op.create_table(
        "paper_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("paper_id", sa.String(length=128), nullable=False),
        sa.Column("chunk_type", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding_id", sa.String(length=256), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["paper_id"], ["papers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_paper_chunks_chunk_type", "paper_chunks", ["chunk_type"])
    op.create_index("ix_paper_chunks_embedding_id", "paper_chunks", ["embedding_id"])
    op.create_index("ix_paper_chunks_paper_id", "paper_chunks", ["paper_id"])

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("paper_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["paper_id"], ["papers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_processing_jobs_paper_id", "processing_jobs", ["paper_id"])
    op.create_index("ix_processing_jobs_priority", "processing_jobs", ["priority"])
    op.create_index("ix_processing_jobs_status", "processing_jobs", ["status"])

    op.create_table(
        "paper_metrics",
        sa.Column("paper_id", sa.String(length=128), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False),
        sa.Column("searches", sa.Integer(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=True),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["paper_id"], ["papers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("paper_id"),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("interests", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("topic_clusters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reading_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("paper_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["paper_id"], ["papers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "paper_id", name="uq_user_paper_history"),
    )
    op.create_index("ix_reading_history_paper_id", "reading_history", ["paper_id"])
    op.create_index("ix_reading_history_user_id", "reading_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_reading_history_user_id", table_name="reading_history")
    op.drop_index("ix_reading_history_paper_id", table_name="reading_history")
    op.drop_table("reading_history")
    op.drop_table("user_profiles")
    op.drop_table("paper_metrics")
    op.drop_index("ix_processing_jobs_status", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_priority", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_paper_id", table_name="processing_jobs")
    op.drop_table("processing_jobs")
    op.drop_index("ix_paper_chunks_paper_id", table_name="paper_chunks")
    op.drop_index("ix_paper_chunks_embedding_id", table_name="paper_chunks")
    op.drop_index("ix_paper_chunks_chunk_type", table_name="paper_chunks")
    op.drop_table("paper_chunks")
    op.execute("DROP INDEX IF EXISTS ix_papers_search_vector")
    op.drop_index("ix_papers_contributions_gin", table_name="papers")
    op.drop_index("ix_papers_topics_gin", table_name="papers")
    op.drop_index("ix_papers_title", table_name="papers")
    op.drop_index("ix_papers_created_at", table_name="papers")
    op.drop_index("ix_papers_arxiv_id", table_name="papers")
    op.drop_table("papers")
