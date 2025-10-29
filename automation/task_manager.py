import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class AutomationTask:
    """Data class for automation tasks"""
    id: str
    task_type: str
    url: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    scheduled_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    task_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    webhook_url: Optional[str] = None

class TaskDatabase:
    """Database handler for automation tasks"""
    
    def __init__(self, db_path: str = "automation_tasks.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    scheduled_at TEXT,
                    executed_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    task_data TEXT,
                    tags TEXT,
                    webhook_url TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """)
    
    def save_task(self, task: AutomationTask):
        """Save or update a task in the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks (
                    id, task_type, url, description, priority, status,
                    created_at, updated_at, scheduled_at, executed_at, completed_at,
                    result, error_message, retry_count, max_retries,
                    task_data, tags, webhook_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id, task.task_type, task.url, task.description,
                task.priority.value, task.status.value,
                task.created_at.isoformat(), task.updated_at.isoformat(),
                task.scheduled_at.isoformat() if task.scheduled_at else None,
                task.executed_at.isoformat() if task.executed_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.result) if task.result else None,
                task.error_message, task.retry_count, task.max_retries,
                json.dumps(task.task_data) if task.task_data else None,
                json.dumps(task.tags) if task.tags else None,
                task.webhook_url
            ))
    
    def get_task(self, task_id: str) -> Optional[AutomationTask]:
        """Retrieve a task by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_task(row)
            return None
    
    def get_tasks(self, status: Optional[TaskStatus] = None, limit: int = 100) -> List[AutomationTask]:
        """Retrieve tasks, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if status:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                    (status.value, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
            
            return [self._row_to_task(row) for row in cursor.fetchall()]
    
    def _row_to_task(self, row: sqlite3.Row) -> AutomationTask:
        """Convert database row to AutomationTask object"""
        return AutomationTask(
            id=row['id'],
            task_type=row['task_type'],
            url=row['url'],
            description=row['description'],
            priority=TaskPriority(row['priority']),
            status=TaskStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            scheduled_at=datetime.fromisoformat(row['scheduled_at']) if row['scheduled_at'] else None,
            executed_at=datetime.fromisoformat(row['executed_at']) if row['executed_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            result=json.loads(row['result']) if row['result'] else None,
            error_message=row['error_message'],
            retry_count=row['retry_count'],
            max_retries=row['max_retries'],
            task_data=json.loads(row['task_data']) if row['task_data'] else None,
            tags=json.loads(row['tags']) if row['tags'] else None,
            webhook_url=row['webhook_url']
        )
    
    def log_task_event(self, task_id: str, level: str, message: str):
        """Log a task event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO task_logs (task_id, timestamp, level, message) VALUES (?, ?, ?, ?)",
                (task_id, datetime.now().isoformat(), level, message)
            )

class TaskScheduler:
    """Task scheduling and management system"""
    
    def __init__(self, db_path: str = "automation_tasks.db"):
        self.db = TaskDatabase(db_path)
        self.scheduler_thread = None
        self.running = False
    
    def create_task(
        self,
        task_type: str,
        url: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        scheduled_at: Optional[datetime] = None,
        task_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        webhook_url: Optional[str] = None
    ) -> str:
        """Create a new automation task"""
        
        task_id = f"task_{int(time.time() * 1000)}"
        now = datetime.now()
        
        task = AutomationTask(
            id=task_id,
            task_type=task_type,
            url=url,
            description=description,
            priority=priority,
            status=TaskStatus.SCHEDULED if scheduled_at else TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            scheduled_at=scheduled_at,
            task_data=task_data,
            tags=tags,
            webhook_url=webhook_url
        )
        
        self.db.save_task(task)
        self.db.log_task_event(task_id, "INFO", "Task created")
        
        logger.info(f"Created task {task_id}: {description}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and details"""
        task = self.db.get_task(task_id)
        if not task:
            return None
        
        return {
            'id': task.id,
            'status': task.status.value,
            'description': task.description,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'executed_at': task.executed_at.isoformat() if task.executed_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'result': task.result,
            'error_message': task.error_message,
            'retry_count': task.retry_count
        }
    
    def get_all_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks, optionally filtered by status"""
        task_status = TaskStatus(status) if status else None
        tasks = self.db.get_tasks(status=task_status)
        
        return [
            {
                'id': task.id,
                'task_type': task.task_type,
                'url': task.url,
                'description': task.description,
                'priority': task.priority.value,
                'status': task.status.value,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat(),
                'scheduled_at': task.scheduled_at.isoformat() if task.scheduled_at else None,
                'result': task.result,
                'error_message': task.error_message
            }
            for task in tasks
        ]

# Global task scheduler instance
task_scheduler = TaskScheduler()