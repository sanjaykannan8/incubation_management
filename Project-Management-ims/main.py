from fastapi import FastAPI, Request, HTTPException
from database import Database
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("transactions.log"),
        logging.StreamHandler()
    ]
)
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

@app.get("/")
async def root():
    return {"message": "Hello World"}   

class Project(BaseModel):
    projectname: str
    description: str
    due_date: str
    owner_id: int

@app.post("/create_project")
async def create_project(project: Project):
    db = None
    try:
        db = Database()
        if db.create_project(project.projectname, project.description, project.owner_id, project.due_date):
            return JSONResponse(content={"message": "Project created"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Project creation failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error creating project: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()
    
    
class Task(BaseModel):
    title: str
    description: str
    project_id: int
    priority: str = "Medium"  # Low, Medium, High, Critical
    status: str = "To Do"
    due_date: str = None
    assigned_to: int = None

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    priority: str = None
    status: str = None
    due_date: str = None
    assigned_to: int = None

@app.get("/projects")
async def get_projects():
    db = None
    try:
        db = Database()
        logging.info("Fetching all projects")
        projects = db.get_projects()
        return {"message": projects}
    except Exception as e:
        logging.error(f"Database error fetching projects: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()
    

@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    db = None
    try:
        db = Database()
        logging.info(f"Fetching project with ID: {project_id}")
        project = db.get_project(project_id=project_id)
        if project:
            return {"message": project}
        else:
            return JSONResponse(content={"error": "Project not found"}, status_code=404)
    except Exception as e:
        logging.error(f"Database error fetching project {project_id}: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()
    
@app.post("/projectstatus")
async def update_project_status(request: Request):
    db = None
    try:
        db = Database()
        data = await request.json()
        project_id = data.get("project_id", None)
        status = data.get("status", None)
        
        if not project_id or not status:
            return JSONResponse(content={"error": "Missing project_id or status"}, status_code=400)
            
        if db.update_project_status(project_id=project_id, status=status):
            return JSONResponse(content={"message": "Project status updated"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Project status update failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error updating project status: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

@app.post("/delete_project")
async def delete_project(request: Request):
    db = None
    try:
        db = Database()
        data = await request.json()
        project_id = data.get("project_id", None)
        
        if not project_id:
            return JSONResponse(content={"error": "Missing project_id"}, status_code=400)
            
        if db.delete_project(project_id=project_id):
            return JSONResponse(content={"message": "Project deleted"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Project deletion failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error deleting project: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

# Task Management Endpoints

@app.post("/create_task")
async def create_task(task: Task):
    db = None
    try:
        db = Database()
        if db.addtask(
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            status=task.status,
            due_date=task.due_date,
            assigned_to=task.assigned_to
        ):
            return JSONResponse(content={"message": "Task created successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Task creation failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error creating task: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

@app.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: int):
    db = None
    try:
        db = Database()
        logging.info(f"Fetching tasks for project {project_id}")
        tasks = db.get_tasks(project_id=project_id)
        if tasks is not None:
            return {"message": tasks}
        else:
            return JSONResponse(content={"error": "Failed to fetch tasks"}, status_code=500)
    except Exception as e:
        logging.error(f"Database error fetching tasks for project {project_id}: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

@app.get("/tasks/{task_id}/{project_id}")
async def get_task(task_id: int,project_id: int):
    db = None
    try:
        db = Database()
        logging.info(f"Fetching task with ID: {task_id}")
        
        task = db.get_task(task_id=task_id,project_id=project_id)
        if task:
            return {"message": task}
        else:
            return JSONResponse(content={"error": "Task not found"}, status_code=404)
    except Exception as e:
        logging.error(f"Database error fetching task {task_id}: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate):
    db = None
    try:
        db = Database()
        logging.info(f"Updating task {task_id}")
        if db.update_task(
            task_id=task_id,
            title=task_update.title,
            description=task_update.description,
            priority=task_update.priority,
            status=task_update.status,
            due_date=task_update.due_date,
            assigned_to=task_update.assigned_to
        ):
            return JSONResponse(content={"message": "Task updated successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Task update failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error updating task {task_id}: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

@app.post("/taskstatus")
async def update_task_status(request: Request):
    db = None
    try:
        db = Database()
        data = await request.json()
        task_id = data.get("task_id", None)
        status = data.get("status", None)
        
        if not task_id or not status:
            return JSONResponse(content={"error": "Missing task_id or status"}, status_code=400)
            
        if db.update_task_status(task_id=task_id, status=status):
            return JSONResponse(content={"message": "Task status updated"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Task status update failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error updating task status: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

@app.post("/delete_task")
async def delete_task(request: Request):
    db = None
    try:
        db = Database()
        data = await request.json()
        task_id = data.get("task_id", None)
        
        if not task_id:
            return JSONResponse(content={"error": "Missing task_id"}, status_code=400)
            
        if db.delete_task(task_id=task_id):
            return JSONResponse(content={"message": "Task deleted"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Task deletion failed"}, status_code=400)
    except Exception as e:
        logging.error(f"Database error deleting task: {e}")
        return JSONResponse(content={"error": "Database error occurred"}, status_code=500)
    finally:
        if db:
            db.close_connection()

# Additional utility endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = None
    try:
        # Test database connection
        db = Database()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}, 
            status_code=500
        )
    finally:
        if db:
            db.close_connection()

@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "api_name": "Project Management API",
        "version": "1.0.0",
        "endpoints": {
            "projects": {
                "GET /projects": "Get all projects",
                "GET /projects/{project_id}": "Get specific project",
                "POST /create_project": "Create new project",
                "POST /projectstatus": "Update project status",
                "POST /delete_project": "Delete project"
            },
            "tasks": {
                "GET /projects/{project_id}/tasks": "Get all tasks for a project",
                "GET /tasks/{task_id}": "Get specific task",
                "POST /create_task": "Create new task",
                "PUT /tasks/{task_id}": "Update task details",
                "POST /taskstatus": "Update task status",
                "POST /delete_task": "Delete task"
            },
            "utility": {
                "GET /": "Root endpoint",
                "GET /health": "Health check",
                "GET /api/info": "API information"
            }
        }
    }


