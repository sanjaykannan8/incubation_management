# Student Management System - Backend

This is the FastAPI backend for the Student Management System.

## Files Structure

- `main.py` - Main FastAPI application with all API endpoints
- `database.py` - Database configuration and connection utilities
- `init_db.py` - Database initialization script
- `reset_database.py` - Database reset utilities
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration for the backend
- `openapi.yaml` - OpenAPI/Swagger specification
- `postman.py` - Postman API testing scripts

## API Endpoints

### Students Management
- `POST /students/register` - Register new student
- `GET /students/{student_id}` - Get specific student
- `GET /admin/students/all` - Get all students
- `GET /admin/students/filter` - Filter students by criteria
- `GET /admin/students/departments` - Get all departments
- `GET /admin/students/batch-years` - Get all batch years
- `GET /admin/students/statuses` - Get all statuses

### Mentors Management
- `POST /mentors/register` - Register new mentor
- `GET /mentors/{mentor_id}` - Get specific mentor
- `GET /admin/mentors/all` - Get all mentors

### Events Management
- `POST /events/create` - Create new event
- `GET /events/{event_id}` - Get specific event
- `GET /admin/events/all` - Get all events

### Certificates Management
- `POST /student_certificates/issue` - Issue certificate
- `GET /student_certificates/{certificate_id}` - Get certificate

### Database Management
- `GET /admin/statistics` - Database statistics
- `GET /admin/database-info` - Database information
- `GET /admin/tables` - Database tables

## Running the Backend

### With Docker (Recommended)
```bash
# From the root directory
docker compose up -d
```

### Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database

PostgreSQL database with the following tables:
- students
- mentors
- events
- student_certificates
- leaderboard_entries
- alumni
- feedbacks
- event_participants
