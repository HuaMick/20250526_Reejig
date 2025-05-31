"""
Pytest configuration and shared fixtures for tests.
"""
import os
import pytest
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector import Error

@pytest.fixture(scope="session")
def prod_db_config():
    """Return production database configuration from environment variables."""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': os.getenv('MYSQL_PORT', '3306'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE', 'onet_data')
    }

@pytest.fixture(scope="session")
def test_db_config():
    """Return test database configuration from environment variables."""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': os.getenv('MYSQL_PORT', '3306'),
        'user': os.getenv('MYSQL_TEST_USER', os.getenv('MYSQL_USER')),
        'password': os.getenv('MYSQL_TEST_PASSWORD', os.getenv('MYSQL_PASSWORD')),
        'database': os.getenv('MYSQL_TEST_DATABASE', 'onet_test_data')
    }

@pytest.fixture(scope="session")
def test_db_connection(test_db_config):
    """Create a MySQL connection to the test database."""
    try:
        connection = mysql.connector.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database']
        )
        yield connection
        connection.close()
    except Error as e:
        pytest.skip(f"Could not connect to test database: {e}")

@pytest.fixture(scope="session")
def test_db_engine(test_db_config):
    """Create a SQLAlchemy engine for the test database."""
    db_config = test_db_config
    engine_url = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    try:
        engine = create_engine(engine_url)
        yield engine
        engine.dispose()
    except Exception as e:
        pytest.skip(f"Could not create test database engine: {e}")

@pytest.fixture(scope="function")
def use_test_db():
    """Temporarily override environment variables to use test database."""
    # Save original environment variables
    original_env = {
        'MYSQL_USER': os.environ.get('MYSQL_USER'),
        'MYSQL_PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'MYSQL_DATABASE': os.environ.get('MYSQL_DATABASE')
    }
    
    # Set environment variables to test database values
    os.environ['MYSQL_USER'] = os.environ.get('MYSQL_TEST_USER', os.environ.get('MYSQL_USER'))
    os.environ['MYSQL_PASSWORD'] = os.environ.get('MYSQL_TEST_PASSWORD', os.environ.get('MYSQL_PASSWORD'))
    os.environ['MYSQL_DATABASE'] = os.environ.get('MYSQL_TEST_DATABASE', 'onet_test_data')
    
    yield
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

@pytest.fixture(scope="module")
def check_api_credentials():
    """Fixture to check if O*NET API credentials are set"""
    if not os.getenv("ONET_USERNAME") or not os.getenv("ONET_PASSWORD"):
        pytest.skip("O*NET API credentials not set, skipping tests that require API fallback") 