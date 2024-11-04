from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from app.core.config import settings
import sys
import psycopg

def test_database_connection():
    """Test the database connection using our settings."""
    try:
        # Print configuration (with sensitive data masked)
        print("\nDatabase Configuration:")
        print(f"Server: {settings.POSTGRES_SERVER}")
        print(f"Port: {settings.POSTGRES_PORT}")
        print(f"Database: {settings.POSTGRES_DB}")
        print(f"User: {settings.POSTGRES_USER}")

        # First test direct connection with psycopg3
        print("\nTesting direct connection with psycopg3...")
        conn_params = {
            "dbname": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD.get_secret_value(),
            "host": settings.POSTGRES_SERVER,
            "port": settings.POSTGRES_PORT
        }
        
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"\nDirect connection successful! 🎉")
                print(f"PostgreSQL version: {version}")

        # Now test SQLAlchemy connection
        print("\nTesting SQLAlchemy connection...")
        url = URL.create(
            drivername="postgresql+psycopg",
            username=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD.get_secret_value(),
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB
        )

        engine = create_engine(
            url,
            echo=True,  # SQL logging
            pool_pre_ping=True,  # Enable connection health checks
            pool_size=5,  # Maximum number of connections to keep
            max_overflow=10  # Maximum number of connections that can be created beyond pool_size
        )
        
        # Test connection
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print("\nSQLAlchemy connection successful! 🎉")
            print(f"PostgreSQL version: {version}")
            
            # Test schema access
            result = connection.execute(text("SELECT current_database(), current_schema();"))
            db, schema = result.fetchone()
            print(f"\nCurrent database: {db}")
            print(f"Current schema: {schema}")
            
            # Test permissions
            print("\nTesting permissions...")
            result = connection.execute(text("""
                SELECT 
                    has_database_privilege(current_user, current_database(), 'CONNECT'),
                    has_schema_privilege(current_user, current_schema(), 'USAGE')
            """))
            db_connect, schema_usage = result.fetchone()
            print(f"Database CONNECT privilege: {db_connect}")
            print(f"Schema USAGE privilege: {schema_usage}")
            
    except Exception as e:
        print("\n❌ Connection failed!")
        print(f"\nError type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if isinstance(e, psycopg.OperationalError):
            print("\nPossible connection issues:")
            print("1. Check if PostgreSQL is running")
            print("2. Verify database exists:")
            print("   psql -U postgres -c 'CREATE DATABASE pokemon_tcg_analyzer;'")
            print("3. Check connection settings in .env file")
            print("4. Ensure password is correct")
            print("5. Check pg_hba.conf for proper authentication settings")
        
        sys.exit(1)

if __name__ == "__main__":
    test_database_connection()