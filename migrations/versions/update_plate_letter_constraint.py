"""update plate letter constraint

Revision ID: update_plate_letter_constraint
Revises: 
Create Date: 2024-04-22 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_plate_letter_constraint'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop the old constraint
    op.drop_constraint('plate_letter_format', 'license_plates', type_='check')
    
    # Add the new constraint
    op.create_check_constraint(
        'plate_letter_format',
        'license_plates',
        "plateLetter REGEXP '^[A-Z]{1,3}$'"
    )

def downgrade():
    # Drop the new constraint
    op.drop_constraint('plate_letter_format', 'license_plates', type_='check')
    
    # Add back the old constraint
    op.create_check_constraint(
        'plate_letter_format',
        'license_plates',
        "plateLetter REGEXP '^[ابجدرسصطعفقلمنهوي]{1,3}$'"
    ) 