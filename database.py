"""
Database configuration and connection management.

This module provides the database engine, session factory, and base model class
for SQLAlchemy ORM operations.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (Railway/production should provide DATABASE_URL)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Normalize Postgres URL for SQLAlchemy if needed
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg2://", 1
    )

# Create database engine
# check_same_thread=False is only needed for SQLite to allow multiple threads
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # check_same_thread=False is only needed for SQLite to allow multiple threads
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
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
