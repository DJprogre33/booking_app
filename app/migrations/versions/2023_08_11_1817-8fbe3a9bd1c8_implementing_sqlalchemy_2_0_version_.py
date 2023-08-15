"""implementing sqlalchemy 2.0 version mapped columns

Revision ID: 8fbe3a9bd1c8
Revises: e08623a99b19
Create Date: 2023-08-11 18:17:56.425287

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8fbe3a9bd1c8"
down_revision = "e08623a99b19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("bookings", "date_to", existing_type=sa.DATE(), nullable=False)
    op.create_index(op.f("ix_bookings_id"), "bookings", ["id"], unique=False)
    op.alter_column(
        "hotels",
        "services",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        nullable=False,
    )
    op.create_index(op.f("ix_hotels_id"), "hotels", ["id"], unique=False)
    op.alter_column(
        "refresh_sessions",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.create_index(
        op.f("ix_refresh_sessions_id"), "refresh_sessions", ["id"], unique=False
    )
    op.create_index(op.f("ix_rooms_id"), "rooms", ["id"], unique=False)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_rooms_id"), table_name="rooms")
    op.drop_index(op.f("ix_refresh_sessions_id"), table_name="refresh_sessions")
    op.alter_column(
        "refresh_sessions",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.drop_index(op.f("ix_hotels_id"), table_name="hotels")
    op.alter_column(
        "hotels",
        "services",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        nullable=True,
    )
    op.drop_index(op.f("ix_bookings_id"), table_name="bookings")
    op.alter_column("bookings", "date_to", existing_type=sa.DATE(), nullable=True)
    # ### end Alembic commands ###
