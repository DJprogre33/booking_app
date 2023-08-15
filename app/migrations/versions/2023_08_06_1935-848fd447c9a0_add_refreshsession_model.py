"""add RefreshSession model

Revision ID: 848fd447c9a0
Revises: 1e7e2640581c
Create Date: 2023-08-06 19:35:09.940251

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "848fd447c9a0"
down_revision = "1e7e2640581c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("refresh_token", sa.UUID(), nullable=True),
        sa.Column("expires_in", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refresh_sessions_refresh_token"),
        "refresh_sessions",
        ["refresh_token"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_refresh_sessions_refresh_token"), table_name="refresh_sessions"
    )
    op.drop_table("refresh_sessions")
    # ### end Alembic commands ###
