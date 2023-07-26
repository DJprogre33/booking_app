"""Bookings on delete cascade room_id

Revision ID: 1e7e2640581c
Revises: 2926e3c6ede0
Create Date: 2023-07-26 13:30:32.929684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e7e2640581c'
down_revision = '2926e3c6ede0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('bookings_room_id_fkey', 'bookings', type_='foreignkey')
    op.create_foreign_key(None, 'bookings', 'rooms', ['room_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bookings', type_='foreignkey')
    op.create_foreign_key('bookings_room_id_fkey', 'bookings', 'rooms', ['room_id'], ['id'])
    # ### end Alembic commands ###
