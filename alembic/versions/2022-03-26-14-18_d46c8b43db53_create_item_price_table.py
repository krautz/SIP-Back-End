"""Create 'item_price' table

Revision ID: d46c8b43db53
Revises: e0325f5877d6
Create Date: 2022-03-26 14:18:51.473269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d46c8b43db53"
down_revision = "e0325f5877d6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "item_price", 
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("item_id", sa.String(length=150), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("price_usd", sa.Float, nullable=False),
    )
    op.create_foreign_key(
        constraint_name="fk__item_price__item",
        source_table="item_price",
        referent_table="item",
        local_cols=["item_id"],
        remote_cols=["market_hash_name"],
        ondelete="CASCADE",
    )
    op.create_index(
        index_name="idx__item_price__date",
        table_name="item_price",
        columns=["date"],
    )
    op.create_unique_constraint(
        constraint_name="unique__item_price__date__item_id",
        table_name="item_price",
        columns=["item_id", "date"],
    )

def downgrade():
    op.drop_table("item_price")
