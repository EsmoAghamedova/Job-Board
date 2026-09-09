"""Add saved jobs.

Revision ID: a91b4c7d6e20
Revises: 7c1f8e4b2a90
"""
from alembic import op
import sqlalchemy as sa


revision = "a91b4c7d6e20"
down_revision = "7c1f8e4b2a90"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "saved_job",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["job.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="unique_saved_job"),
    )
    with op.batch_alter_table("saved_job", schema=None) as batch_op:
        batch_op.create_index("ix_saved_job_user_id", ["user_id"])
        batch_op.create_index("ix_saved_job_job_id", ["job_id"])


def downgrade():
    op.drop_table("saved_job")
