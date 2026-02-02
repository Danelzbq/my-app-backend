"""
Database structure checker - Verify database schema matches models.

Use this to diagnose database structure issues.
"""
import os
from sqlalchemy import inspect

def check_database():
    """Check if database structure matches the models."""
    print("=" * 60)
    print("DATABASE STRUCTURE CHECKER")
    print("=" * 60)
    
    try:
        import database
        import models
        
        db_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
        print(f"\nDatabase: {db_url}")
        
        # Get expected columns from models
        expected_posts_columns = {
            'id', 'type', 'title', 'content', 'excerpt', 'author', 
            'tags', 'cover_url', 'image_urls', 'created_at', 'owner_id'
        }
        
        # Get actual columns from database
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        
        print(f"\nExisting tables: {', '.join(tables)}")
        
        if 'posts' in tables:
            actual_columns = {col['name'] for col in inspector.get_columns('posts')}
            
            print(f"\n{'Column':<20} {'Status':<15} {'Type':<20}")
            print("-" * 60)
            
            all_columns = expected_posts_columns | actual_columns
            for col in sorted(all_columns):
                if col in expected_posts_columns and col in actual_columns:
                    col_info = next(c for c in inspector.get_columns('posts') if c['name'] == col)
                    status = "✓ OK"
                    col_type = str(col_info['type'])
                elif col in expected_posts_columns:
                    status = "✗ MISSING"
                    col_type = "N/A"
                else:
                    status = "? EXTRA"
                    col_info = next(c for c in inspector.get_columns('posts') if c['name'] == col)
                    col_type = str(col_info['type'])
                
                print(f"{col:<20} {status:<15} {col_type:<20}")
            
            missing = expected_posts_columns - actual_columns
            extra = actual_columns - expected_posts_columns
            
            print("\n" + "=" * 60)
            if missing:
                print(f"✗ MISSING COLUMNS: {', '.join(missing)}")
                print("  → You need to reset the database!")
                print("  → Run: python reset_database.py")
            elif extra:
                print(f"? EXTRA COLUMNS: {', '.join(extra)}")
                print("  → Old columns that are no longer used")
            else:
                print("✓ Database structure is correct!")
            print("=" * 60)
            
        else:
            print("\n✗ 'posts' table does not exist!")
            print("  → Run: python reset_database.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
