import psycopg2
import os


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST", "localhost"),
            database=os.getenv("DATABASE_NAME", "studentmanagement"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "Priya@0572"),
            port=os.getenv("DATABASE_PORT", "5432")
        )
        self.cursor = self.conn.cursor()

    def create_all_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                phone TEXT,
                batch_year INT,
                department TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at TIMESTAMPTZ DEFAULT now()
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mentors (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                phone TEXT,
                title TEXT,
                expertise TEXT[],
                available BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at TIMESTAMPTZ DEFAULT now()
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_certificates (
                id INTEGER PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                certificate_title TEXT NOT NULL,
                description TEXT,
                issued_by INTEGER REFERENCES mentors(id),
                issued_at TIMESTAMPTZ DEFAULT now(),
                certificate_data JSONB
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                starts_at TIMESTAMPTZ,
                ends_at TIMESTAMPTZ,
                location TEXT,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_by INTEGER REFERENCES mentors(id),
                created_at TIMESTAMPTZ DEFAULT now()
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_participants (
                id INTEGER PRIMARY KEY,
                event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                role TEXT DEFAULT 'attendee',
                status TEXT DEFAULT 'registered',
                registered_at TIMESTAMPTZ DEFAULT now(),
                UNIQUE(event_id, student_id)
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard_entries (
                id INTEGER PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                metric TEXT NOT NULL,
                score NUMERIC DEFAULT 0,
                context JSONB,
                updated_at TIMESTAMPTZ DEFAULT now(),
                UNIQUE(student_id, metric)
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alumni (
                id INTEGER PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE UNIQUE,
                graduation_year INT,
                current_status TEXT
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY,
                from_student INTEGER REFERENCES students(id),
                from_mentor INTEGER REFERENCES mentors(id),
                target_type TEXT NOT NULL,
                target_id INTEGER,
                rating SMALLINT,
                comment TEXT,
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        ''')
        self.conn.commit()

if __name__ == "__main__":
    db = Database()
    db.create_all_tables()

