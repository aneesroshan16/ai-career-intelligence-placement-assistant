"""add extensive resume fields

Revision ID: 0003_resume_fields
Revises: 0002_target_role
Create Date: 2026-08-11 15:28:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0003_resume_fields'
down_revision = '0002_target_role'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to resumes
    op.add_column('resumes', sa.Column('name', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('email', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('github_url', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('linkedin_url', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('portfolio_url', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('achievements', postgresql.ARRAY(sa.String()), nullable=True))

    # Add category to resume_skills
    op.add_column('resume_skills', sa.Column('category', sa.String(), nullable=True))

    # Create resume_experience table
    op.create_table('resume_experience',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('company', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('is_current', sa.Boolean(), nullable=False, default=False),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('resume_experience')
    op.drop_column('resume_skills', 'category')
    op.drop_column('resumes', 'achievements')
    op.drop_column('resumes', 'portfolio_url')
    op.drop_column('resumes', 'linkedin_url')
    op.drop_column('resumes', 'github_url')
    op.drop_column('resumes', 'phone')
    op.drop_column('resumes', 'email')
    op.drop_column('resumes', 'name')
