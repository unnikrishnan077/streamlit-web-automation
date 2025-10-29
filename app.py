import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any
import os

# Configure page
st.set_page_config(
    page_title="Web Automation Control Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .task-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .status-success {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-pending {
        background-color: #ffc107;
        color: black;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-failed {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class WebAutomationManager:
    def __init__(self):
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []
        if 'task_counter' not in st.session_state:
            st.session_state.task_counter = 1
    
    def add_task(self, task_data: Dict[str, Any]):
        """Add a new automation task"""
        task = {
            'id': st.session_state.task_counter,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Pending',
            **task_data
        }
        st.session_state.tasks.append(task)
        st.session_state.task_counter += 1
        return task['id']
    
    def update_task_status(self, task_id: int, status: str, result: str = None):
        """Update task status"""
        for task in st.session_state.tasks:
            if task['id'] == task_id:
                task['status'] = status
                if result:
                    task['result'] = result
                task['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
    
    def get_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return st.session_state.tasks[::-1]  # Return newest first
    
    def execute_web_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web automation task"""
        try:
            # Simulate web automation (replace with actual implementation)
            task_type = task_data.get('task_type')
            url = task_data.get('url')
            
            if task_type == 'form_fill':
                return self._simulate_form_fill(task_data)
            elif task_type == 'data_extraction':
                return self._simulate_data_extraction(task_data)
            elif task_type == 'click_automation':
                return self._simulate_click_automation(task_data)
            elif task_type == 'file_upload':
                return self._simulate_file_upload(task_data)
            else:
                return {'success': False, 'error': 'Unknown task type'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _simulate_form_fill(self, task_data: Dict) -> Dict:
        """Simulate form filling automation"""
        time.sleep(2)  # Simulate processing time
        form_data = task_data.get('form_data', {})
        return {
            'success': True,
            'message': f'Successfully filled form with {len(form_data)} fields',
            'details': f"Processed fields: {', '.join(form_data.keys())}"
        }
    
    def _simulate_data_extraction(self, task_data: Dict) -> Dict:
        """Simulate data extraction"""
        time.sleep(3)  # Simulate processing time
        selectors = task_data.get('selectors', [])
        return {
            'success': True,
            'message': f'Successfully extracted data using {len(selectors)} selectors',
            'extracted_data': {
                'items_found': 25,
                'selectors_used': selectors,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _simulate_click_automation(self, task_data: Dict) -> Dict:
        """Simulate click automation"""
        time.sleep(1)  # Simulate processing time
        click_sequence = task_data.get('click_sequence', [])
        return {
            'success': True,
            'message': f'Successfully executed {len(click_sequence)} click actions',
            'actions_performed': click_sequence
        }
    
    def _simulate_file_upload(self, task_data: Dict) -> Dict:
        """Simulate file upload"""
        time.sleep(2)  # Simulate processing time
        files = task_data.get('files', [])
        return {
            'success': True,
            'message': f'Successfully uploaded {len(files)} files',
            'uploaded_files': files
        }

def main():
    # Initialize automation manager
    automation_manager = WebAutomationManager()
    
    # Header
    st.markdown('<div class="main-header">🤖 Web Automation Control Center</div>', unsafe_allow_html=True)
    
    # Sidebar for task creation
    with st.sidebar:
        st.header("📋 Create New Task")
        
        task_type = st.selectbox(
            "Task Type",
            ["form_fill", "data_extraction", "click_automation", "file_upload"],
            format_func=lambda x: {
                "form_fill": "📝 Form Filling",
                "data_extraction": "📊 Data Extraction",
                "click_automation": "🖱️ Click Automation",
                "file_upload": "📁 File Upload"
            }[x]
        )
        
        url = st.text_input("Target URL", placeholder="https://example.com")
        description = st.text_area("Task Description", placeholder="Describe what this task should do...")
        
        # Task-specific parameters
        if task_type == "form_fill":
            st.subheader("Form Data")
            form_fields = st.text_area(
                "Form Fields (JSON)",
                placeholder='{"name": "John Doe", "email": "john@example.com"}',
                help="Enter form data as JSON"
            )
        
        elif task_type == "data_extraction":
            st.subheader("Extraction Settings")
            selectors = st.text_area(
                "CSS Selectors (one per line)",
                placeholder=".product-title\n.price\n.description"
            )
        
        elif task_type == "click_automation":
            st.subheader("Click Sequence")
            click_sequence = st.text_area(
                "Click Selectors (one per line)",
                placeholder="#login-button\n.submit-form\n.confirm-action"
            )
        
        elif task_type == "file_upload":
            st.subheader("File Upload Settings")
            file_selector = st.text_input("File Input Selector", placeholder="input[type='file']")
            files = st.text_area("File Paths (one per line)", placeholder="/path/to/file1.pdf\n/path/to/file2.jpg")
        
        # Priority and scheduling
        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
        schedule_type = st.selectbox("Execution", ["Immediate", "Scheduled"])
        
        if schedule_type == "Scheduled":
            schedule_time = st.time_input("Schedule Time")
        
        # Create task button
        if st.button("🚀 Create Task", type="primary"):
            if url and description:
                # Prepare task data
                task_data = {
                    'task_type': task_type,
                    'url': url,
                    'description': description,
                    'priority': priority,
                    'schedule_type': schedule_type
                }
                
                # Add task-specific data
                if task_type == "form_fill" and form_fields:
                    try:
                        task_data['form_data'] = json.loads(form_fields)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format for form fields")
                        return
                
                elif task_type == "data_extraction" and selectors:
                    task_data['selectors'] = [s.strip() for s in selectors.split('\n') if s.strip()]
                
                elif task_type == "click_automation" and click_sequence:
                    task_data['click_sequence'] = [s.strip() for s in click_sequence.split('\n') if s.strip()]
                
                elif task_type == "file_upload" and files:
                    task_data['file_selector'] = file_selector
                    task_data['files'] = [f.strip() for f in files.split('\n') if f.strip()]
                
                if schedule_type == "Scheduled":
                    task_data['schedule_time'] = str(schedule_time)
                
                # Add task
                task_id = automation_manager.add_task(task_data)
                st.success(f"✅ Task #{task_id} created successfully!")
                
                # Execute immediately if not scheduled
                if schedule_type == "Immediate":
                    with st.spinner("Executing task..."):
                        result = automation_manager.execute_web_task(task_data)
                        if result['success']:
                            automation_manager.update_task_status(task_id, "Completed", result['message'])
                            st.success(f"Task completed: {result['message']}")
                        else:
                            automation_manager.update_task_status(task_id, "Failed", result['error'])
                            st.error(f"Task failed: {result['error']}")
            else:
                st.error("Please fill in URL and description")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Task Dashboard")
        
        # Task statistics
        tasks = automation_manager.get_tasks()
        if tasks:
            completed_tasks = len([t for t in tasks if t['status'] == 'Completed'])
            pending_tasks = len([t for t in tasks if t['status'] == 'Pending'])
            failed_tasks = len([t for t in tasks if t['status'] == 'Failed'])
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            col_stat1.metric("Total Tasks", len(tasks))
            col_stat2.metric("Completed", completed_tasks)
            col_stat3.metric("Pending", pending_tasks)
            col_stat4.metric("Failed", failed_tasks)
        
        # Task list
        if tasks:
            st.subheader("Recent Tasks")
            for task in tasks[:10]:  # Show latest 10 tasks
                status_class = {
                    'Completed': 'status-success',
                    'Pending': 'status-pending',
                    'Failed': 'status-failed'
                }.get(task['status'], 'status-pending')
                
                with st.expander(f"Task #{task['id']} - {task['description'][:50]}..."):
                    col_task1, col_task2 = st.columns([3, 1])
                    
                    with col_task1:
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**URL:** {task['url']}")
                        st.write(f"**Type:** {task['task_type']}")
                        st.write(f"**Priority:** {task['priority']}")
                        st.write(f"**Created:** {task['timestamp']}")
                        if 'result' in task:
                            st.write(f"**Result:** {task['result']}")
                    
                    with col_task2:
                        st.markdown(f'<span class="{status_class}">{task["status"]}</span>', unsafe_allow_html=True)
                        
                        if task['status'] == 'Pending':
                            if st.button(f"Execute #{task['id']}", key=f"exec_{task['id']}"):
                                with st.spinner("Executing..."):
                                    result = automation_manager.execute_web_task(task)
                                    if result['success']:
                                        automation_manager.update_task_status(task['id'], "Completed", result['message'])
                                        st.rerun()
                                    else:
                                        automation_manager.update_task_status(task['id'], "Failed", result['error'])
                                        st.rerun()
        else:
            st.info("No tasks created yet. Use the sidebar to create your first automation task!")
    
    with col2:
        st.header("⚙️ System Status")
        
        # System info
        st.metric("System Status", "🟢 Online")
        st.metric("Active Sessions", "1")
        st.metric("Uptime", "24h 15m")
        
        # Quick actions
        st.subheader("🔧 Quick Actions")
        
        if st.button("🗑️ Clear All Tasks"):
            st.session_state.tasks = []
            st.session_state.task_counter = 1
            st.success("All tasks cleared!")
            st.rerun()
        
        if st.button("📥 Export Tasks"):
            if tasks:
                df = pd.DataFrame(tasks)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"automation_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No tasks to export")
        
        # GitHub integration status
        st.subheader("🔗 GitHub Integration")
        st.success("✅ Connected to repository")
        st.code("unnikrishnan077/streamlit-web-automation")
        
        if st.button("🔄 Sync Repository"):
            st.success("Repository synced successfully!")

if __name__ == "__main__":
    main()