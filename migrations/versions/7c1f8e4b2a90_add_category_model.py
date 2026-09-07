"""Add normalized category model

Revision ID: 7c1f8e4b2a90
Revises: 3813350db351
"""
from alembic import op
import sqlalchemy as sa


revision = "7c1f8e4b2a90"
down_revision = "3813350db351"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    with op.batch_alter_table("category", schema=None) as batch_op:
        batch_op.create_index("ix_category_name", ["name"], unique=True)

    connection = op.get_bind()
    connection.execute(sa.text(
        "INSERT INTO category (name) "
        "SELECT DISTINCT category FROM job WHERE category IS NOT NULL"
    ))
    for name in ("IT", "Design", "Marketing", "Finance", "Sales", "Engineering", "Other"):
        connection.execute(sa.text(
            "INSERT INTO category (name) SELECT :name "
            "WHERE NOT EXISTS (SELECT 1 FROM category WHERE category.name = :name)"
        ), {"name": name})

    with op.batch_alter_table("job", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("category_id", sa.Integer(), nullable=True))

    connection.execute(sa.text(
        "UPDATE job SET category_id = (SELECT id FROM category "
        "WHERE category.name = job.category)"
    ))

    with op.batch_alter_table("job", schema=None) as batch_op:
        batch_op.alter_column(
            "category_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key("fk_job_category_id", "category", [
                                    "category_id"], ["id"])
        batch_op.drop_column("category")


def downgrade():
    with op.batch_alter_table("job", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("category", sa.String(length=80), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE job SET category = (SELECT name FROM category "
        "WHERE category.id = job.category_id)"
    ))

    with op.batch_alter_table("job", schema=None) as batch_op:
        batch_op.alter_column(
            "category", existing_type=sa.String(length=80), nullable=False)
        batch_op.drop_constraint("fk_job_category_id", type_="foreignkey")
        batch_op.drop_column("category_id")

    op.drop_table("category")
