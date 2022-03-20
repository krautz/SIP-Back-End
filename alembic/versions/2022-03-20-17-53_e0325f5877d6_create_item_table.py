"""Create 'item' table

Revision ID: e0325f5877d6
Revises: 632649756bb6
Create Date: 2022-03-20 17:53:19.094074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e0325f5877d6"
down_revision = "632649756bb6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "item", 
        sa.Column("market_hash_name", sa.String(length=150), primary_key=True),
        sa.Column("app_id", sa.Integer, nullable=False),
        sa.Column("name_pt", sa.String(length=150), nullable=True),
        sa.Column("name_en", sa.String(length=150), nullable=True),
    )

def downgrade():
    op.drop_table("item")
