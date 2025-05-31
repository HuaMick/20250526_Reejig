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
        'database': os.getenv('MYSQL_TEST_DATABASE', 'onet_test_db')
    }
