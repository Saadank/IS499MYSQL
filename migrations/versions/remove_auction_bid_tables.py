"""remove auction, bid, and offer tables

Revision ID: remove_auction_bid_tables
Revises: previous_migration_id
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_auction_bid_tables'
down_revision = 'previous_migration_id'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the bids table first (due to foreign key constraint)
    op.drop_table('bids')
    # Drop the auctions table
    op.drop_table('auctions')
    # Drop the offers table
    op.drop_table('offers')
    # Remove auction_start_price and minimum_offer_price columns from license_plates table
    op.drop_column('license_plates', 'auction_start_price')
    op.drop_column('license_plates', 'minimum_offer_price')
    # Remove AUCTION and OFFERS from ListingType enum
    op.execute("ALTER TABLE license_plates MODIFY listing_type ENUM('buy_now')")

def downgrade():
    # Recreate the auctions table
    op.create_table('auctions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plate_id', sa.Integer(), nullable=False),
        sa.Column('start_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('winner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['plate_id'], ['license_plates.plateID'], ),
        sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate the bids table
    op.create_table('bids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('auction_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate the offers table
    op.create_table('offers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plate_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('offer_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plate_id'], ['license_plates.plateID'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add back auction_start_price and minimum_offer_price columns to license_plates table
    op.add_column('license_plates', sa.Column('auction_start_price', sa.Float(), nullable=True))
    op.add_column('license_plates', sa.Column('minimum_offer_price', sa.Float(), nullable=True))
    # Add back AUCTION and OFFERS to ListingType enum
    op.execute("ALTER TABLE license_plates MODIFY listing_type ENUM('buy_now', 'auction', 'offers')") 