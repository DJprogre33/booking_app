"""alter field image_id rename wirh image_path in Hotels

Revision ID: 241c1f0a861f
Revises: db82d4e39868
Create Date: 2023-07-20 16:22:14.513534

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '241c1f0a861f'
down_revision = 'db82d4e39868'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hotels', sa.Column('image_path', sa.String(), nullable=False))
    op.drop_column('hotels', 'image_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hotels', sa.Column('image_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('hotels', 'image_path')
    # ### end Alembic commands ###