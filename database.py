"""
Database configuration and connection management.

This module provides the database engine, session factory, and base model class
for SQLAlchemy ORM operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL - uses a local file-based database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Create database engine
# check_same_thread=False is only needed for SQLite to allow multiple threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True for SQL query debugging
    pool_pre_ping=True  # Verify connections before using them
)

# Session factory for database operations
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Base class for all database models
Base = declarative_base()
