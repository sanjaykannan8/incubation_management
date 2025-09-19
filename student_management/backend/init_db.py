#!/usr/bin/env python3
"""
Database initialization script for Docker
"""
import time
import sys
from database import Database

def wait_for_db():
    """Wait for database to be ready"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            db = Database()
            print(" Database connection successful!")
            return db
        except Exception as e:
            retry_count += 1
            print(f"Waiting for database... (attempt {retry_count}/{max_retries})")
            print(f"Error: {e}")
            time.sleep(2)
    
    print("Could not connect to database after maximum retries")
    sys.exit(1)

def main():
    print("Initializing Student Management Database...")
    
    # Wait for database to be ready
    db = wait_for_db()
    
    # Create all tables
    try:
        db.create_all_tables()
        print("All database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)
    
    print("🎉 Database initialization completed!")

if __name__ == "__main__":
    main()
