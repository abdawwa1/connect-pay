"""foreign-key-on-payment

Revision ID: d095092ed86d
Revises: 3633992e88b4
Create Date: 2023-09-17 16:26:01.006478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd095092ed86d'
down_revision: Union[str, None] = '3633992e88b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'payment', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_column('payment', 'user_id')
    # ### end Alembic commands ###
