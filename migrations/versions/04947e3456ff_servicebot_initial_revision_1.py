"""ServiceBot Initial revision 1

Revision ID: 04947e3456ff
Revises: 
Create Date: 2024-11-04 16:54:27.096237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04947e3456ff'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('active_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.Column('type_group', sa.String(length=64), nullable=True),
    sa.Column('access_flag', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='service_bot'
    )
    op.create_table('temporary_request_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tg', sa.BigInteger(), nullable=False),
    sa.Column('clinic_name', sa.String(length=512), nullable=True),
    sa.Column('city', sa.String(length=128), nullable=True),
    sa.Column('apparat_name', sa.String(length=512), nullable=True),
    sa.Column('description_problem', sa.String(length=4096), nullable=True),
    sa.Column('phone_number', sa.String(length=1024), nullable=True),
    sa.Column('mediafiles', sa.JSON(), nullable=True),
    sa.Column('company_details', sa.String(length=4096), nullable=True),
    sa.Column('location', sa.String(length=4096), nullable=True),
    sa.Column('maintenance_date', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='service_bot'
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tg', sa.BigInteger(), nullable=True),
    sa.Column('nickname', sa.String(length=64), nullable=True),
    sa.Column('fullname', sa.String(length=64), nullable=True),
    sa.Column('date_reg', sa.DateTime(), nullable=True),
    sa.Column('message_thread_id', sa.BigInteger(), nullable=True),
    sa.Column('access_flag', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='service_bot'
    )
    op.create_table('created_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('date_creation', sa.DateTime(), nullable=True),
    sa.Column('clinic_name', sa.String(length=512), nullable=True),
    sa.Column('city', sa.String(length=128), nullable=True),
    sa.Column('apparat_name', sa.String(length=512), nullable=True),
    sa.Column('description_problem', sa.String(length=4096), nullable=True),
    sa.Column('phone_number', sa.String(length=1024), nullable=True),
    sa.Column('mediafiles', sa.JSON(), nullable=True),
    sa.Column('company_details', sa.String(length=4096), nullable=True),
    sa.Column('location', sa.String(length=4096), nullable=True),
    sa.Column('maintenance_date', sa.String(length=512), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['service_bot.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='service_bot'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('created_requests', schema='service_bot')
    op.drop_table('users', schema='service_bot')
    op.drop_table('temporary_request_data', schema='service_bot')
    op.drop_table('active_groups', schema='service_bot')
    # ### end Alembic commands ###
