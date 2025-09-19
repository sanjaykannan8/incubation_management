import psycopg2
import logging

# Use the logger configured in main.py instead of setting up a new one
logger = logging.getLogger(__name__)



class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        try:
            import os
            db_host = os.getenv('DB_HOST', 'localhost')
            db_name = os.getenv('DB_NAME', 'projectmanagement')
            db_user = os.getenv('DB_USER', 'imsadmin')
            db_password = os.getenv('DB_PASSWORD', 'howareyou')
            db_port = os.getenv('DB_PORT', '5432')
            
            self.conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=db_port
            )
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to the database successfully at {db_host}:{db_port}")
            
            # Create tables if they don't exist
            self.create_table()
            
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            self.conn = None
            self.cursor = None
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {e}")
            self.conn = None
            self.cursor = None
    
    def close_connection(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
                self.cursor = None
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                self.conn = None
            logger.info("Database connection closed successfully")
        except psycopg2.Error as e:
            logger.error(f"Error closing database connection: {e}")
        except Exception as e:
            logger.error(f"Unexpected error closing database connection: {e}")
    
    def __del__(self):
        self.close_connection()
    
    def _check_connection(self):
        """Check if database connection is available"""
        if not self.conn or not self.cursor:
            logger.error("Database connection not available")
            return False
        return True
        
    def create_table(self):
        """Create all necessary tables for the project management system"""
        if not self.conn or not self.cursor:
            logger.error("Database connection not available for table creation")
            return False
            
        try:
            # 1. roles
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    role_id SERIAL PRIMARY KEY,
                    role_name VARCHAR(50) UNIQUE NOT NULL
                );
            """)
            
            # 2. users
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role_id INT REFERENCES roles(role_id) ON DELETE SET NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # 3. projects
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id SERIAL PRIMARY KEY,
                    project_name VARCHAR(150) NOT NULL,
                    description TEXT,
                    owner_id INT DEFAULT 1,
                    start_date DATE,
                    due_date DATE,
                    status VARCHAR(20) DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # 4. project_members
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_members (
                    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
                    user_id INT DEFAULT 1,
                    role_in_project VARCHAR(50),
                    PRIMARY KEY (project_id, user_id)
                );
            """)
            
            # 5. tasks
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id SERIAL PRIMARY KEY,
                    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
                    assigned_to INT DEFAULT 1,
                    title VARCHAR(150) NOT NULL,
                    description TEXT,
                    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
                    status VARCHAR(20) DEFAULT 'To Do',
                    start_date DATE,
                    due_date DATE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # 6. task_tags
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    tag_id SERIAL PRIMARY KEY,
                    tag_name VARCHAR(50) UNIQUE NOT NULL
                );
            """)
            
            # 7. task_tag_map
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_tag_map (
                    task_id INT REFERENCES tasks(task_id) ON DELETE CASCADE,
                    tag_id INT REFERENCES task_tags(tag_id) ON DELETE CASCADE,
                    PRIMARY KEY (task_id, tag_id)
                );
            """)
            
            self.conn.commit()  
            logger.info("All tables created successfully!")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error creating tables: {e}")
            if self.conn:
                self.conn.rollback()
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error during table creation: {e}")
            if self.conn:
                self.conn.rollback()
            return False

        
        
    def get_projects(self, user_id=1):
        """Retrieve all projects for a specific user"""
        if not self._check_connection():
            return None
            
        try:
            self.cursor.execute("""
                SELECT * FROM projects WHERE owner_id = %s
            """, (user_id,))
            projects = self.cursor.fetchall()
            project_list = []
            for project in projects:
                project_list.append({
                    "project_id": project[0],
                    "project_name": project[1],
                    "description": project[2],
                    "owner_id": project[3],
                    "start_date": project[4],
                    "due_date": project[5],
                    "status": project[6],
                    "created_at": project[7]
                })
            logger.info(f"Retrieved {len(project_list)} projects for user {user_id}")
            return project_list
            
        except psycopg2.Error as e:
            logger.error(f"Error retrieving projects for user {user_id}: {e}")
            if self.conn:
                self.conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving projects: {e}")
            if self.conn:
                self.conn.rollback()
            return None
         
            
    def get_project(self, user_id=1, project_id=1):
        """Retrieve a specific project by ID for a user"""
        try:
            self.cursor.execute("""
                SELECT * FROM projects WHERE project_id = %s AND owner_id = %s
            """, (project_id, user_id))
            project = self.cursor.fetchone()
            
            if project:
                project_data = {
                    "project_id": project[0],
                    "project_name": project[1],
                    "description": project[2],
                    "owner_id": project[3],
                    "start_date": project[4],
                    "due_date": project[5],
                    "status": project[6],
                    "created_at": project[7]
                }
                logger.info(f"Retrieved project {project_id} for user {user_id}")
                return project_data
            else:
                logger.warning(f"Project {project_id} not found for user {user_id}")
                return None
                
        except psycopg2.Error as e:
            logger.error(f"Error retrieving project {project_id} for user {user_id}: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving project: {e}")
            self.conn.rollback()
            return None
    
    def create_project(self, projectname, description, owner_id=1, due_date=None):
        """Create a new project"""
        if not self._check_connection():
            return False
            
        try:
            if due_date:
                self.cursor.execute("""
                    INSERT INTO projects (project_name, description, owner_id, due_date, start_date) 
                    VALUES (%s, %s, %s, %s, CURRENT_DATE)
                """, (projectname, description, owner_id, due_date))
            else:
                self.cursor.execute("""
                    INSERT INTO projects (project_name, description, owner_id, start_date) 
                    VALUES (%s, %s, %s, CURRENT_DATE)
                """, (projectname, description, owner_id))
            self.conn.commit()
            logger.info(f"Project '{projectname}' created successfully for user {owner_id}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error creating project '{projectname}': {e}")
            if self.conn:
                self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    def update_project_status(self, project_id, status):
        """Update the status of a project"""
        try:
            with self.cursor as cursor:
                cursor.execute("""
                    UPDATE projects SET status = %s WHERE project_id = %s
                """, (status, project_id))
            self.conn.commit()
            if cursor.rowcount == 0:
                    logger.warning(f"No project found with ID {project_id} to update")
                    return False
                    
            logger.info(f"Project {project_id} status updated to '{status}'")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error updating project {project_id} status: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating project status: {e}")
            self.conn.rollback()
            return False
    def addtask(self, project_id, title, description, priority, status, due_date, assigned_to):
        """Add a new task to a project"""
        try:
            with self.cursor as cursor:
                cursor.execute("""
                    INSERT INTO tasks (project_id, title, description, priority, status, due_date, assigned_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (project_id, title, description, priority, status, due_date, assigned_to))
            self.conn.commit()
            logger.info(f"Task '{title}' added to project {project_id}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error adding task '{title}' to project {project_id}: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding task: {e}")
            self.conn.rollback()
            return False
    
    def delete_project(self, project_id):
        """Delete a project and all associated tasks"""
        try:
            with self.cursor as cursor:
                cursor.execute("""
                    DELETE FROM projects WHERE project_id = %s
                """, (project_id,))
            self.conn.commit()
            if cursor.rowcount == 0:
                    logger.warning(f"No project found with ID {project_id} to delete")
                    return False
                    
            logger.info(f"Project {project_id} deleted successfully")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting project: {e}")
            self.conn.rollback()
            return False
    def delete_task(self, task_id):
        """Delete a specific task"""
        try:
            with self.cursor as cursor:
                cursor.execute("""
                    DELETE FROM tasks WHERE task_id = %s
                """, (task_id,))
            self.conn.commit()
            if cursor.rowcount == 0:
                    logger.warning(f"No task found with ID {task_id} to delete")
                    return False
                    
            logger.info(f"Task {task_id} deleted successfully")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting task: {e}")
            self.conn.rollback()
            return False

    def get_tasks(self, project_id):
        """Get all tasks for a specific project"""
        try:
            self.cursor.execute("""
                SELECT * FROM tasks WHERE project_id = %s
            """, (project_id,))
            tasks = self.cursor.fetchall()
            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task[0],
                    "project_id": task[1],
                    "assigned_to": task[2],
                    "title": task[3],
                    "description": task[4],
                    "priority": task[5],
                    "status": task[6],
                    "start_date": task[7],
                    "due_date": task[8],
                    "created_at": task[9]
                })
            logger.info(f"Retrieved {len(task_list)} tasks for project {project_id}")
            return task_list
            
        except psycopg2.Error as e:
            logger.error(f"Error retrieving tasks for project {project_id}: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving tasks: {e}")
            self.conn.rollback()
            return None

    def get_task(self, task_id,project_id):
        """Get a specific task by ID"""
        try:
            self.cursor.execute("""
                SELECT * FROM tasks WHERE task_id = %s AND project_id = %s
            """, (task_id,project_id))
            task = self.cursor.fetchone()
            
            if task:
                task_data = {
                    "task_id": task[0],
                    "project_id": task[1],
                    "assigned_to": task[2],
                    "title": task[3],
                    "description": task[4],
                    "priority": task[5],
                    "status": task[6],
                    "start_date": task[7],
                    "due_date": task[8],
                    "created_at": task[9]
                }
                logger.info(f"Retrieved task {task_id}")
                return task_data
            else:
                logger.warning(f"Task {task_id} not found")
                return None
                
        except psycopg2.Error as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving task: {e}")
            self.conn.rollback()
            return None

    def update_task_status(self, task_id, status):
        """Update the status of a task"""
        try:
            with self.cursor as cursor:
                cursor.execute("""
                    UPDATE tasks SET status = %s WHERE task_id = %s
                """, (status, task_id))
            self.conn.commit()
            if cursor.rowcount == 0:
                    logger.warning(f"No task found with ID {task_id} to update")
                    return False
                    
            logger.info(f"Task {task_id} status updated to '{status}'")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error updating task {task_id} status: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating task status: {e}")
            self.conn.rollback()
            return False

    def update_task(self, task_id, title=None, description=None, priority=None, status=None, due_date=None, assigned_to=None):
        """Update task details"""
        try:
            update_fields = []
            values = []
            
            if title is not None:
                update_fields.append("title = %s")
                values.append(title)
            if description is not None:
                update_fields.append("description = %s")
                values.append(description)
            if priority is not None:
                update_fields.append("priority = %s")
                values.append(priority)
            if status is not None:
                update_fields.append("status = %s")
                values.append(status)
            if due_date is not None:
                update_fields.append("due_date = %s")
                values.append(due_date)
            if assigned_to is not None:
                update_fields.append("assigned_to = %s")
                values.append(assigned_to)
            
            if not update_fields:
                logger.warning("No fields to update")
                return False
                
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE task_id = %s"
            
            with self.cursor as cursor:
                cursor.execute(query, values)
            self.conn.commit()
            
            if cursor.rowcount == 0:
                logger.warning(f"No task found with ID {task_id} to update")
                return False
                
            logger.info(f"Task {task_id} updated successfully")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error updating task {task_id}: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating task: {e}")
            self.conn.rollback()
            return False
