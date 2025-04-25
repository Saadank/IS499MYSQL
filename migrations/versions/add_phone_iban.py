"""add phone number and iban

Revision ID: add_phone_iban
Revises: previous_migration_id
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_phone_iban'
down_revision = 'previous_migration_id'
branch_labels = None
depends_on = None

def upgrade():
    # Add phone_number column (not nullable)
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=False))
    # Add iban column (nullable)
    op.add_column('users', sa.Column('iban', sa.String(34), nullable=True))

def downgrade():
    # Remove the columns
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'iban') 