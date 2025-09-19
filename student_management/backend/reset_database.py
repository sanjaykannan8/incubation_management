import psycopg2

def reset_database():
    conn = psycopg2.connect(
        host="localhost",
        database="studentmanagement",
        user="postgres",
        password="Priya@0572"
    )
    cursor = conn.cursor()
    
    # Drop all tables in correct order (considering foreign keys)
    drop_tables = [
        "DROP TABLE IF EXISTS feedbacks CASCADE;",
        "DROP TABLE IF EXISTS alumni CASCADE;",
        "DROP TABLE IF EXISTS leaderboard_entries CASCADE;",
        "DROP TABLE IF EXISTS event_participants CASCADE;",
        "DROP TABLE IF EXISTS events CASCADE;",
        "DROP TABLE IF EXISTS student_certificates CASCADE;",
        "DROP TABLE IF EXISTS certificates CASCADE;",
        "DROP TABLE IF EXISTS mentors CASCADE;",
        "DROP TABLE IF EXISTS students CASCADE;",
        "DROP TABLE IF EXISTS users CASCADE;"
    ]
    
    print("Dropping existing tables...")
    for drop_sql in drop_tables:
        cursor.execute(drop_sql)
        print(f"Executed: {drop_sql}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("All tables dropped successfully!")
    
    # Now create new tables with integer IDs
    print("Creating new tables with integer IDs...")
    from database import Database
    db = Database()
    db.create_all_tables()
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()
