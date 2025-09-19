import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
import json
import logging
import time
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("transactions.log")
    ]
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Read request body before processing (if needed for logging)
    body = b""
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        # Create a new request with the body for downstream processing
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive

    # Log request details
    logging.info(f"New Request: {request.method} {request.url} {request.client.host} {request.client.port}")

    response = await call_next(request)
    
    # Log response time
    process_time = (time.time() - start_time) * 1000
    body_str = body.decode('utf-8') if body else ""
    logging.info(
        f"Completed: {request.method} {request.url} - Body: {body_str[:100]}{'...' if len(body_str) > 100 else ''} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}ms"
    )

    return response
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        database=os.getenv("DATABASE_NAME", "studentmanagement"),
        user=os.getenv("DATABASE_USER", "postgres"),
        password=os.getenv("DATABASE_PASSWORD", "Priya@0572"),
        port=os.getenv("DATABASE_PORT", "5432")
    )
    return conn


@app.get("/")
async def root():
    return {
        "message": "Student Management System API",
        "version": "2.0.0",
        "endpoints": {
            "students": "/students/register, /students/{student_id}",
            "mentors": "/mentors/register, /mentors/{mentor_id}",
            "events": "/events/create, /events/{event_id}",
            "student_certificates": "/student_certificates/issue, /student_certificates/{student_certificate_id}",
            "leaderboard": "/leaderboard/add, /leaderboard/{entry_id}",
            "alumni": "/alumni/register, /alumni/{alumni_id}",
            "feedbacks": "/feedbacks/add, /feedbacks/{feedback_id}",
            "docs": "/docs"
        },
        "note": "All endpoints now require manual ID assignment. No auto-generated IDs."
    }



# -------------------------
# STUDENTS APIs
# -------------------------
class Student(BaseModel):
    id: int
    email: str
    password_hash: str
    full_name: str
    phone: str
    batch_year: int = None
    department: str = None

class StudentRegistration(BaseModel):
    email: str
    password_hash: str
    full_name: str
    phone: str
    batch_year: int = None
    department: str = None

@app.post("/students/register")
async def register_student(student: StudentRegistration):
    logger.info(f"Registering student: {student.email}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (email, password_hash, full_name, phone, batch_year, department)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, (student.email, student.password_hash, student.full_name, student.phone, student.batch_year, student.department))

        student_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Student registered successfully: {student.email}, id: {student_id}")
        return {"message": "Student registered successfully", "student_id": student_id}
    except Exception as e:
        logger.error(f"Error registering student {student.email}: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/students/{student_id}")
async def get_student(student_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students WHERE id = %s;", (student_id,))
        student = cur.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Convert tuple to dict
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, student))
    finally:
        cur.close()
        conn.close()


# -------------------------
# EVENTS APIs
# -------------------------
class EventCreate(BaseModel):
    title: str
    description: str = None
    starts_at: str = None
    ends_at: str = None
    location: str = None
    created_by: int  # mentor_id

class Event(BaseModel):
    id: int
    title: str
    description: str = None
    starts_at: str = None
    ends_at: str = None
    location: str = None
    created_by: int  # mentor_id


@app.post("/events/create")
async def create_event(event: EventCreate):
    logger.info(f"Creating event: {event.title}")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO events (title, description, starts_at, ends_at, location, created_by)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, (event.title, event.description, event.starts_at, event.ends_at, event.location, event.created_by))

        event_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Event created successfully: {event.title}, id: {event_id}")
        return {"message": "Event created successfully", "event_id": event_id}
    except Exception as e:
        logger.error(f"Error creating event {event.title}: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/events/{event_id}")
async def get_event(event_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM events WHERE id = %s;", (event_id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, event))
    finally:
        cur.close()
        conn.close()


# -------------------------
# MENTORS APIs
# -------------------------
class Mentor(BaseModel):
    id: int
    email: str
    password_hash: str
    full_name: str
    phone: str
    title: str = None
    expertise: list[str] = None
    available: bool = True

class MentorRegistration(BaseModel):
    email: str
    password_hash: str
    full_name: str
    phone: str
    title: str = None
    expertise: list[str] = None
    available: bool = True

@app.post("/mentors/register")
async def register_mentor(mentor: MentorRegistration):
    logger.info(f"Registering mentor: {mentor.email}")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO mentors (email, password_hash, full_name, phone, title, expertise, available)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (mentor.email, mentor.password_hash, mentor.full_name, mentor.phone, mentor.title, mentor.expertise, mentor.available))
        mentor_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Mentor registered successfully: {mentor.email}, id: {mentor_id}")
        return {"message": "Mentor registered successfully", "mentor_id": mentor_id}
    except Exception as e:
        logger.error(f"Error registering mentor {mentor.email}: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/mentors/{mentor_id}")
async def get_mentor(mentor_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM mentors WHERE id = %s;", (mentor_id,))
        mentor = cur.fetchone()
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, mentor))
    finally:
        cur.close()
        conn.close()



# -------------------------
# STUDENT CERTIFICATES APIs
# -------------------------
class StudentCertificateCreate(BaseModel):
    student_id: int
    certificate_title: str
    description: str = None
    issued_by: int  # mentor_id
    certificate_data: dict = None

class StudentCertificate(BaseModel):
    id: int
    student_id: int
    certificate_title: str
    description: str = None
    issued_by: int  # mentor_id
    certificate_data: dict = None

@app.post("/student_certificates/issue")
async def issue_student_certificate(student_certificate: StudentCertificateCreate):
    logger.info(f"Issuing student certificate for student: {student_certificate.student_id}")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO student_certificates (student_id, certificate_title, description, issued_by, certificate_data)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (student_certificate.student_id, student_certificate.certificate_title, student_certificate.description, student_certificate.issued_by, json.dumps(student_certificate.certificate_data) if student_certificate.certificate_data else None))
        sc_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Student certificate issued successfully: {student_certificate.student_id}, id: {sc_id}")
        return {"message": "Student certificate issued successfully", "student_certificate_id": sc_id}
    except Exception as e:
        logger.error(f"Error issuing student certificate for student {student_certificate.student_id}: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/student_certificates/{student_certificate_id}")
async def get_student_certificate(student_certificate_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM student_certificates WHERE id = %s;", (student_certificate_id,))
        sc = cur.fetchone()
        if not sc:
            raise HTTPException(status_code=404, detail="Student certificate not found")
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, sc))
    finally:
        cur.close()
        conn.close()


# -------------------------
# LEADERBOARD APIs
# -------------------------
class LeaderboardEntry(BaseModel):
    id: int
    student_id: int
    metric: str
    score: float = 0
    context: dict = None

@app.post("/leaderboard/add")
async def add_leaderboard_entry(entry: LeaderboardEntry):
    logger.info(f"Adding leaderboard entry for student: {entry.student_id}, metric: {entry.metric}")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO leaderboard_entries (id, student_id, metric, score, context)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (entry.id, entry.student_id, entry.metric, entry.score, json.dumps(entry.context) if entry.context else None))
        entry_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Leaderboard entry added successfully: {entry.student_id}, id: {entry_id}")
        return {"message": "Leaderboard entry added successfully", "entry_id": entry_id}
    except Exception as e:
        logger.error(f"Error adding leaderboard entry for student {entry.student_id}: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/leaderboard/{entry_id}")
async def get_leaderboard_entry(entry_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM leaderboard_entries WHERE id = %s;", (entry_id,))
        entry = cur.fetchone()
        if not entry:
            raise HTTPException(status_code=404, detail="Leaderboard entry not found")
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, entry))
    finally:
        cur.close()
        conn.close()


# -------------------------
# ALUMNI APIs
# -------------------------
class Alumni(BaseModel):
    id: int
    student_id: int
    graduation_year: int
    current_status: str = None

@app.post("/alumni/register")
async def register_alumni(alumni: Alumni):
    logger.info(f"Registering alumni for student: {alumni.student_id}")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # First check if student exists
        cur.execute("SELECT id FROM students WHERE id = %s;", (alumni.student_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=400, detail=f"Student with ID {alumni.student_id} does not exist")
        
        # Check if student is already registered as alumni
        cur.execute("SELECT id FROM alumni WHERE student_id = %s;", (alumni.student_id,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail=f"Student {alumni.student_id} is already registered as alumni")
        
        # Insert new alumni record
        cur.execute("""
            INSERT INTO alumni (id, student_id, graduation_year, current_status)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """, (alumni.id, alumni.student_id, alumni.graduation_year, alumni.current_status))
        alumni_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Alumni registered successfully: {alumni.student_id}, id: {alumni_id}")
        return {"message": "Alumni registered successfully", "alumni_id": alumni_id}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Error registering alumni for student {alumni.student_id}: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/alumni/{alumni_id}")
async def get_alumni(alumni_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM alumni WHERE id = %s;", (alumni_id,))
        alumni = cur.fetchone()
        if not alumni:
            raise HTTPException(status_code=404, detail="Alumni not found")
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, alumni))
    finally:
        cur.close()
        conn.close()


# -------------------------
# FEEDBACK APIs
# -------------------------
class Feedback(BaseModel):
    id: int
    from_student: int = None  # student_id
    from_mentor: int = None   # mentor_id  
    target_type: str
    target_id: int = None
    rating: int = None
    comment: str = None
    metadata: dict = None

@app.post("/feedbacks/add")
async def add_feedback(feedback: Feedback):
    logger.info(f"Adding feedback from student: {feedback.from_student}, mentor: {feedback.from_mentor}")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO feedbacks (id, from_student, from_mentor, target_type, target_id, rating, comment, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (feedback.id, feedback.from_student, feedback.from_mentor, feedback.target_type, feedback.target_id, feedback.rating, feedback.comment, json.dumps(feedback.metadata) if feedback.metadata else None))
        feedback_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Feedback added successfully: id: {feedback_id}")
        return {"message": "Feedback added successfully", "feedback_id": feedback_id}
    except Exception as e:
        logger.error(f"Error adding feedback: {e}")
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/feedbacks/{feedback_id}")
async def get_feedback(feedback_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM feedbacks WHERE id = %s;", (feedback_id,))
        feedback = cur.fetchone()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, feedback))
    finally:
        cur.close()
        conn.close()


# -------------------------
# DATABASE MANAGEMENT APIs
# -------------------------

@app.get("/admin/database-info", tags=["Database Management"])
async def get_database_info():
    """Get database connection and basic information"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get database version
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        
        # Get current database name
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()[0]
        
        # Get current user
        cur.execute("SELECT current_user;")
        user = cur.fetchone()[0]
        
        return {
            "database_name": db_name,
            "user": user,
            "postgresql_version": version,
            "status": "Connected successfully"
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/tables", tags=["Database Management"])
async def list_all_tables():
    """List all tables in the database with row counts"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get all table names
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        # Get row count for each table
        table_info = []
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            table_info.append({
                "table_name": table,
                "row_count": count
            })
        
        return {
            "total_tables": len(tables),
            "tables": table_info
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/students/all", tags=["Database Management"])
async def view_all_students():
    """View all students in the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students ORDER BY id;")
        students = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return {
            "total_students": len(students),
            "students": [dict(zip(columns, student)) for student in students]
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/mentors/all", tags=["Database Management"])
async def view_all_mentors():
    """View all mentors in the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM mentors ORDER BY id;")
        mentors = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return {
            "total_mentors": len(mentors),
            "mentors": [dict(zip(columns, mentor)) for mentor in mentors]
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/events/all", tags=["Database Management"])
async def view_all_events():
    """View all events in the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM events ORDER BY id;")
        events = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return {
            "total_events": len(events),
            "events": [dict(zip(columns, event)) for event in events]
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/statistics", tags=["Database Management"])
async def get_database_statistics():
    """Get comprehensive database statistics"""
    try:
        # Use a completely fresh connection with explicit isolation
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST", "localhost"),
            database=os.getenv("DATABASE_NAME", "studentmanagement"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "Priya@0572"),
            port=os.getenv("DATABASE_PORT", "5432")
        )
        conn.autocommit = True  # Use autocommit for this specific connection
        
        stats = {}
        
        # Count records in each table
        tables = ['students', 'mentors', 'events', 'student_certificates', 'leaderboard_entries', 'alumni', 'feedbacks']
        
        with conn.cursor() as cur:
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    stats[f"{table}_count"] = cur.fetchone()[0]
                except Exception as e:
                    print(f"Error counting {table}: {e}")  # Use print instead of logger
                    stats[f"{table}_count"] = 0
            
            # Get recent activity (last 5 students)
            try:
                cur.execute("SELECT id, full_name, email FROM students ORDER BY id DESC LIMIT 5;")
                recent_students = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                stats["recent_students"] = [dict(zip(columns, student)) for student in recent_students]
            except Exception as e:
                print(f"Error getting recent students: {e}")  # Use print instead of logger
                stats["recent_students"] = []
        
        conn.close()
        
        return {
            "database_statistics": stats,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"Database connection error: {e}")  # Use print instead of logger
        return {
            "database_statistics": {
                "students_count": 0,
                "mentors_count": 0,
                "events_count": 0,
                "student_certificates_count": 0,
                "leaderboard_entries_count": 0,
                "alumni_count": 0,
                "feedbacks_count": 0,
                "recent_students": []
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": "Database connection failed"
        }

@app.get("/admin/search/students/{search_term}", tags=["Database Management"])
async def search_students(search_term: str):
    """Search students by name or email"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM students 
            WHERE full_name ILIKE %s OR email ILIKE %s 
            ORDER BY id;
        """, (f"%{search_term}%", f"%{search_term}%"))
        students = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return {
            "search_term": search_term,
            "results_found": len(students),
            "students": [dict(zip(columns, student)) for student in students]
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/students/filter", tags=["Database Management"])
async def filter_students(
    department: str = None,
    batch_year: int = None,
    status: str = None,
    search: str = None
):
    """Filter students by department, batch year, status, or search term"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Build dynamic query
        where_conditions = []
        params = []
        
        if department:
            where_conditions.append("department ILIKE %s")
            params.append(f"%{department}%")
            
        if batch_year:
            where_conditions.append("batch_year = %s")
            params.append(batch_year)
            
        if status:
            where_conditions.append("status ILIKE %s")
            params.append(f"%{status}%")
            
        if search:
            where_conditions.append("(full_name ILIKE %s OR email ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT * FROM students 
            WHERE {where_clause}
            ORDER BY batch_year DESC, full_name;
        """
        
        cur.execute(query, params)
        students = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        return {
            "filters": {
                "department": department,
                "batch_year": batch_year,
                "status": status,
                "search": search
            },
            "results_found": len(students),
            "students": [dict(zip(columns, student)) for student in students]
        }
    finally:
        cur.close()
        conn.close()

@app.get("/admin/students/departments", tags=["Database Management"])
async def get_student_departments():
    """Get all unique departments"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT department FROM students WHERE department IS NOT NULL ORDER BY department;")
        departments = [row[0] for row in cur.fetchall()]
        return {"departments": departments}
    finally:
        cur.close()
        conn.close()

@app.get("/admin/students/batch-years", tags=["Database Management"])
async def get_student_batch_years():
    """Get all unique batch years"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT batch_year FROM students WHERE batch_year IS NOT NULL ORDER BY batch_year DESC;")
        batch_years = [row[0] for row in cur.fetchall()]
        return {"batch_years": batch_years}
    finally:
        cur.close()
        conn.close()

@app.get("/admin/students/statuses", tags=["Database Management"])
async def get_student_statuses():
    """Get all unique student statuses"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT status FROM students WHERE status IS NOT NULL ORDER BY status;")
        statuses = [row[0] for row in cur.fetchall()]
        return {"statuses": statuses}
    finally:
        cur.close()
        conn.close()

@app.delete("/admin/cleanup/test-data", tags=["Database Management"])
async def cleanup_test_data():
    """⚠️ DANGER: Remove all test/demo data (use with caution!)"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Count records before deletion
        tables = ['students', 'mentors', 'events', 'student_certificates', 'leaderboard', 'alumni', 'feedbacks']
        before_counts = {}
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                before_counts[table] = cur.fetchone()[0]
            except:
                before_counts[table] = 0
        
        # Clear all data
        for table in tables:
            try:
                cur.execute(f"DELETE FROM {table};")
            except:
                pass
        
        conn.commit()
        
        return {
            "message": "All test data has been removed",
            "records_deleted": before_counts,
            "warning": "This action cannot be undone"
        }
    finally:
        cur.close()
        conn.close()

