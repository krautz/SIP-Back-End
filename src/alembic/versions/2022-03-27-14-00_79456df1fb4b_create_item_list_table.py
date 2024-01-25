"""Create 'item_list' table

Revision ID: 79456df1fb4b
Revises: d46c8b43db53
Create Date: 2022-03-27 14:00:03.711404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "79456df1fb4b"
down_revision = "d46c8b43db53"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "item_list", 
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("item_id", sa.String(length=150), nullable=False),
        sa.Column("list_id", sa.Integer, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
    )
    op.create_foreign_key(
        constraint_name="fk__item_list__list",
        source_table="item_list",
        referent_table="list",
        local_cols=["list_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        constraint_name="fk__item_list__item",
        source_table="item_list",
        referent_table="item",
        local_cols=["item_id"],
        remote_cols=["market_hash_name"],
        ondelete="CASCADE",
    )
    op.create_index(
        index_name="idx__item_list__list_id",
        table_name="item_list",
        columns=["list_id"],
    )
    op.create_unique_constraint(
        constraint_name="unique__item_list__list_id__item_id",
        table_name="item_list",
        columns=["item_id", "list_id"],
    )


def downgrade():
    op.drop_table("item_list")
