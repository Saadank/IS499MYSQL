from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def run_migrations():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Check if columns exist first
            result = connection.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'license_plates' 
                AND TABLE_SCHEMA = DATABASE()
            """))
            existing_columns = [row[0].lower() for row in result]
            
            # Add columns that don't exist
            if 'city' not in existing_columns:
                connection.execute(text("ALTER TABLE license_plates ADD COLUMN city VARCHAR(50)"))
            
            if 'transfer_cost' not in existing_columns:
                connection.execute(text("ALTER TABLE license_plates ADD COLUMN transfer_cost VARCHAR(50)"))
            
            if 'plate_type' not in existing_columns:
                connection.execute(text("ALTER TABLE license_plates ADD COLUMN plate_type VARCHAR(20)"))
            
            # Check if expires_at column exists in orders table
            result = connection.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'orders' 
                AND TABLE_SCHEMA = DATABASE()
            """))
            existing_columns = [row[0].lower() for row in result]
            
            if 'expires_at' not in existing_columns:
                connection.execute(text("ALTER TABLE orders ADD COLUMN expires_at DATETIME"))
            
            connection.commit()
            print("Migration completed successfully!")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    run_migrations() 