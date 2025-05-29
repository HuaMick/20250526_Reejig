import pytest
from sqlalchemy import create_engine
from src.config.schemas import Base # Assuming your SQLAlchemy Base is in schemas.py
import os

@pytest.fixture(scope="session")
def in_memory_sqlite_engine():
    """Creates an in-memory SQLite database engine for the test session and creates all tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine) # Create all tables defined in your Base
    return engine

@pytest.fixture(scope="function")
def test_db_session(in_memory_sqlite_engine):
    """Provides a session that rolls back changes after each test function."""
    connection = in_memory_sqlite_engine.connect()
    transaction = connection.begin()
    # Optionally, bind a session to this transaction if your functions require a session object
    # from sqlalchemy.orm import sessionmaker
    # Session = sessionmaker(bind=connection)
    # session = Session()

    # Override environment variables for database to point to SQLite for the test duration
    original_env = {}
    env_to_override = {
        "MYSQL_HOST": ":memory:", # Indicate SQLite in-memory
        "MYSQL_DATABASE": "", # SQLite in-memory doesn't use a database name in the same way
        "MYSQL_USER": "",
        "MYSQL_PASSWORD": "",
        "MYSQL_PORT": ""
    }
    for key, value in env_to_override.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield connection # Or session, if you create one

    transaction.rollback()
    connection.close()

    # Restore original environment variables
    for key, value in original_env.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value 