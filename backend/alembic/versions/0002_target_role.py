"""add target_role to student_profiles

Revision ID: 0002_target_role
Revises: 0001_init
Create Date: 2026-08-11 15:27:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_target_role'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('student_profiles', sa.Column('target_role', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('student_profiles', 'target_role')
