# services/users-service/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # Correct import for declarative_base
import redis

# --- Configuration for "No Database Dev Mode" ---
# Set NO_DATABASE_MODE to True to run without a database (uses in-memory data)
# Set NO_DATABASE_MODE to False to use a PostgreSQL database (requires DATABASE_URL)
NO_DB_MODE = os.getenv("NO_DATABASE_MODE", "False").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL") # e.g., "postgresql://user:password@host:port/dbname"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# --- SQLAlchemy Setup (Core) ---
# Base must be defined globally for models.py to import it.
Base = declarative_base()
engine = None
SessionLocal = None
redis_client_prod = None # Initialize redis client for production

# --- Conditional Setup for Database and Redis based on NO_DB_MODE ---
if not NO_DB_MODE:
    # Production mode (Database and Redis are expected)
    if DATABASE_URL:
        try:
            engine = create_engine(DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            # IMPORTANT: Base.metadata.create_all(bind=engine)
            # This line is responsible for creating tables.
            # In a production setup with Alembic, Alembic handles migrations (table creation/alteration).
            # If not using Alembic initially, you might call this once on application startup
            # (e.g., in main.py) to create tables if they don't exist.
            # For now, it's commented out here; decide where to manage table creation.
            # Example: if __name__ == "__main__" in main.py or a startup event.
            # Base.metadata.create_all(bind=engine)
            print("Production mode: PostgreSQL engine and session configured.")
        except Exception as e:
            print(f"Error configuring PostgreSQL for production: {e}")
            engine = None # Ensure engine is None if configuration fails
            SessionLocal = None # Ensure SessionLocal is None if configuration fails
    else:
        print("Production mode (NO_DB_MODE=False), but DATABASE_URL is not set. PostgreSQL will not be available.")

    # Redis for Production Mode
    try:
        redis_client_prod = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        redis_client_prod.ping()
        print(f"Production mode: Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except redis.exceptions.ConnectionError as e:
        print(f"Production mode: Redis connection failed: {e}")
        redis_client_prod = None # Ensure it's None if connection fails
else:
    # Development mode (No Database, No Redis)
    print("Development mode: No database backend (NO_DB_MODE=True). Using in-memory data structures.")
    print("Development mode: Redis will not be used.")
    # engine, SessionLocal, and redis_client_prod remain None as initialized

# --- Unified Access Functions ---
# These functions provide a consistent way to get DB sessions or Redis client,
# respecting the NO_DB_MODE.

def get_db():
    """
    Provides a database session.
    In NO_DB_MODE or if DATABASE_URL is not set, yields None.
    Otherwise, yields a SQLAlchemy session from SessionLocal.
    """
    if NO_DB_MODE or not DATABASE_URL or not SessionLocal:
        # print("Dev Mode or DB not configured: get_db() yielding None.")
        yield None # Ensure the generator yields, even if it's None
    else:
        # print("Prod Mode: get_db() providing DB session.")
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

def get_redis():
    """
    Provides a Redis client.
    In NO_DB_MODE, returns None.
    Otherwise, returns the production Redis client (if connection was successful).
    """
    if NO_DB_MODE:
        # print("Dev Mode: get_redis() returning None.")
        return None
    else:
        # print("Prod Mode: get_redis() providing Redis client.")
        return redis_client_prod

def test_database_connection():
    """
    Tests the database connection if not in NO_DB_MODE and DATABASE_URL is set.
    """
    if NO_DB_MODE or not DATABASE_URL or not engine:
        print("Dev Mode or DB not configured: Database connection test skipped.")
        return True # Simulate success as no DB is expected
    try:
        with engine.connect() as connection:
            print("Successfully connected to the PostgreSQL database (test_database_connection).")
            return True
    except Exception as e:
        print(f"Failed to connect to the PostgreSQL database (test_database_connection): {e}")
        return False

# --- Placeholder for Alembic (Migrations) ---
# When you're ready to use Alembic for database migrations:
# 1. Initialize Alembic in your project (e.g., in the `services/users-service` directory or project root):
#    `alembic init alembic`
# 2. Configure `alembic.ini` with your `DATABASE_URL`.
#    Make sure `sqlalchemy.url` points to your database.
# 3. Modify `alembic/env.py`:
#    - Import `Base` from this `database.py` file:
#      `from database import Base` (adjust path if alembic is outside users-service)
#    - Set `target_metadata = Base.metadata`
# 4. Create your first migration:
#    `alembic revision -m "create_user_related_tables"`
#    Edit the generated script in `alembic/versions/` to define your tables (users, user_profiles, etc.)
#    using `op.create_table(...)`.
# 5. Apply the migration:
#    `alembic upgrade head`
#
# Once Alembic is set up, you should not call `Base.metadata.create_all(bind=engine)`
# as Alembic will manage the database schema.
# ---
