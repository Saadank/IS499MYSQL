"""update plate unique constraint

Revision ID: update_plate_unique_constraint
Revises: update_plate_letter_constraint
Create Date: 2024-04-29 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_plate_unique_constraint'
down_revision = 'update_plate_letter_constraint'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the old unique constraint
    op.drop_constraint('unique_plate_number_letter', 'license_plates', type_='unique')
    
    # Add the new unique constraint that includes plate_type
    op.create_unique_constraint(
        'unique_plate_number_letter_type',
        'license_plates',
        ['plateNumber', 'plateLetter', 'plate_type']
    )

def downgrade():
    # Drop the new constraint
    op.drop_constraint('unique_plate_number_letter_type', 'license_plates', type_='unique')
    
    # Recreate the old constraint
    op.create_unique_constraint(
        'unique_plate_number_letter',
        'license_plates',
        ['plateNumber', 'plateLetter']
    ) 