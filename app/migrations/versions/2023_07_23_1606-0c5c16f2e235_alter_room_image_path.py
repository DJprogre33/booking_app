"""alter room image path

Revision ID: 0c5c16f2e235
Revises: 864203b58c60
Create Date: 2023-07-23 16:06:51.743398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c5c16f2e235'
down_revision = '864203b58c60'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('image_path', sa.String(), nullable=True))
    op.drop_column('rooms', 'image_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('image_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('rooms', 'image_path')
    # ### end Alembic commands ###