"""Create 'list' table

Revision ID: 632649756bb6
Revises: 
Create Date: 2022-03-20 12:57:50.615780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "632649756bb6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "list",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("steam_id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.Date, nullable=False),
        sa.Column("updated_at", sa.Date, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
    )


def downgrade():
    op.drop_table("list")
