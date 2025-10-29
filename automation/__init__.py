"""Web automation package for Streamlit deployment"""

from .task_manager import TaskScheduler, TaskStatus, TaskPriority
from .web_controller import WebAutomationController

__version__ = "1.0.0"
__author__ = "unnikrishnan077"

__all__ = [
    "TaskScheduler",
    "TaskStatus", 
    "TaskPriority",
    "WebAutomationController"
]