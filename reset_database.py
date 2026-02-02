"""
Database reset script - Recreate all tables with the latest schema.

WARNING: This will delete all existing data!
Use this when the database schema has changed and you need to recreate tables.
"""
import os
import sys
from pathlib import Path

def reset_database():
    """Reset the database by dropping and recreating all tables."""
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print("\nWARNING: This will delete ALL existing data!")
    print("Make sure you have a backup if needed.\n")
    
    # Get database path
    db_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    if db_url.startswith("sqlite"):
        db_file = db_url.replace("sqlite:///", "").replace("sqlite://", "")
        db_path = Path(db_file)
        
        if db_path.exists():
            print(f"Found database: {db_path}")
            
            # Create backup
            import datetime
            backup_name = f"{db_path.stem}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
            backup_path = db_path.parent / backup_name
            
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✓ Backup created: {backup_path}")
            
            # Delete old database
            db_path.unlink()
            print(f"✓ Old database deleted: {db_path}")
        else:
            print(f"No existing database found at: {db_path}")
    else:
        print(f"Using database: {db_url}")
        print("Note: For non-SQLite databases, tables will be dropped and recreated.")
    
    # Import models and create tables
    print("\nCreating new database tables...")
    
    try:
        import models
        import database
        
        # Drop all tables first (for non-SQLite)
        if not db_url.startswith("sqlite"):
            models.Base.metadata.drop_all(bind=database.engine)
            print("✓ Old tables dropped")
        
        # Create all tables
        models.Base.metadata.create_all(bind=database.engine)
        print("✓ New tables created successfully!")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        
        print(f"\nCreated tables: {', '.join(tables)}")
        
        # Show Post table structure
        if 'posts' in tables:
            columns = inspector.get_columns('posts')
            print("\nPost table columns:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"  - {col['name']}: {col['type']} ({nullable})")
        
        print("\n" + "=" * 60)
        print("✓ Database reset completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
