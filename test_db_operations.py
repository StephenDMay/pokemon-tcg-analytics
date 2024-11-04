from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, inspect
from sqlalchemy.engine import URL
from app.core.config import settings
import sys

def test_database_operations():
    """Test basic database operations."""
    try:
        # Create SQLAlchemy engine
        url = URL.create(
            drivername="postgresql+psycopg",
            username=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD.get_secret_value(),
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB
        )

        engine = create_engine(url)
        
        with engine.connect() as connection:
            # First, let's see what tables already exist
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            print("\nExisting tables:", existing_tables)
            
            # Create a test table
            print("\nCreating test table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_cards (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    card_type VARCHAR(50),
                    rarity VARCHAR(50)
                )
            """))
            connection.commit()
            
            # Insert some test data
            print("\nInserting test data...")
            connection.execute(text("""
                INSERT INTO test_cards (name, card_type, rarity)
                VALUES 
                    ('Charizard', 'Pokemon', 'Rare'),
                    ('Ultra Ball', 'Trainer', 'Uncommon'),
                    ('Fire Energy', 'Energy', 'Common')
                ON CONFLICT DO NOTHING
            """))
            connection.commit()
            
            # Query the data
            print("\nQuerying test data:")
            result = connection.execute(text("SELECT * FROM test_cards"))
            rows = result.fetchall()
            
            # Print results in a formatted way
            print("\nTest Cards:")
            print("-" * 50)
            print(f"{'ID':<5} {'Name':<20} {'Type':<15} {'Rarity':<15}")
            print("-" * 50)
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15} {row[3]:<15}")
            
            # Get count by card type
            print("\nCard count by type:")
            result = connection.execute(text("""
                SELECT card_type, COUNT(*) as count 
                FROM test_cards 
                GROUP BY card_type
            """))
            for row in result:
                print(f"{row[0]}: {row[1]} cards")
            
            print("\nDatabase operations completed successfully! 🎉")
            
    except Exception as e:
        print("\n❌ Database operation failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_database_operations()