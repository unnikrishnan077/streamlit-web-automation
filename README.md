# 🤖 Streamlit Web Automation System

A powerful web automation platform built with Streamlit that allows you to automate any website tasks and duties. This system provides a user-friendly interface for creating, managing, and executing automated web workflows.

## ✨ Features

- **🎯 Multiple Task Types**: Form filling, data extraction, click automation, and file uploads
- **📅 Task Scheduling**: Execute tasks immediately or schedule them for later
- **⚡ Priority Management**: Organize tasks by priority (Low, Medium, High, Urgent)
- **📊 Real-time Dashboard**: Monitor task status, execution history, and system metrics
- **🔄 Retry Logic**: Automatic retry mechanism for failed tasks
- **📝 Comprehensive Logging**: Detailed logs for debugging and monitoring
- **🔗 GitHub Integration**: Version control and collaborative development
- **☁️ Cloud Ready**: Optimized for Streamlit Community Cloud deployment

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/unnikrishnan077/streamlit-web-automation.git
cd streamlit-web-automation
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

4. **Access the app**:
Open your browser and navigate to `http://localhost:8501`

### 🌐 Deploy on Streamlit Community Cloud

1. **Fork this repository** to your GitHub account
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Click "New app"**
4. **Connect your GitHub repository**:
   - Repository: `your-username/streamlit-web-automation`
   - Branch: `main`
   - Main file path: `app.py`
5. **Click "Deploy"**

Your app will be live at: `https://your-app-name.streamlit.app`

## 📋 Task Types

### 1. 📝 Form Filling
Automate form submissions with predefined data:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello World"
}
```

### 2. 📊 Data Extraction
Extract data using CSS selectors:
```
.product-title
.price
.description
.rating
```

### 3. 🖱️ Click Automation
Perform sequential clicks:
```
#login-button
.submit-form
.confirm-action
```

### 4. 📁 File Upload
Upload files to web forms:
```
/path/to/document.pdf
/path/to/image.jpg
```

## 🏗️ Architecture

```
streamlit-web-automation/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── automation/
│   ├── __init__.py       # Package initialization
│   ├── web_controller.py # Selenium-based automation engine
│   └── task_manager.py   # Task scheduling and database management
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables
You can customize the application behavior using environment variables:

```bash
# Optional: Custom database path
DB_PATH=./custom_tasks.db

# Optional: Default timeout for web operations
WEB_TIMEOUT=30

# Optional: Enable/disable headless mode
HEADLESS_MODE=true
```

### Streamlit Configuration
The app includes optimized Streamlit settings in `.streamlit/config.toml`:
- Arrow serialization for better performance
- Optimized browser settings
- Custom theme colors

## 📊 Database Schema

The application uses SQLite for task persistence:

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    -- ... additional fields
);
```

## 🔒 Security Considerations

- **Headless Execution**: All web automation runs in headless mode for security
- **Input Validation**: All user inputs are validated and sanitized
- **Resource Limits**: Built-in timeouts prevent infinite loops
- **Error Handling**: Comprehensive error catching and logging

## 📝 API Reference

### Task Creation
```python
from automation import TaskScheduler, TaskPriority

scheduler = TaskScheduler()
task_id = scheduler.create_task(
    task_type="form_fill",
    url="https://example.com/contact",
    description="Fill contact form",
    priority=TaskPriority.HIGH,
    task_data={
        "form_data": {"name": "John", "email": "john@example.com"}
    }
)
```

### Task Monitoring
```python
status = scheduler.get_task_status(task_id)
all_tasks = scheduler.get_all_tasks(status="completed")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/unnikrishnan077/streamlit-web-automation/issues) page
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

## 🚀 Roadmap

- [ ] **API Integration**: REST API for programmatic task creation
- [ ] **Webhook Support**: Real-time notifications for task completion
- [ ] **Advanced Scheduling**: Cron-like scheduling capabilities
- [ ] **Multi-browser Support**: Firefox, Safari, Edge support
- [ ] **Cloud Storage**: Integration with AWS S3, Google Drive
- [ ] **Team Collaboration**: Multi-user support and permissions

## 🏆 Use Cases

- **Lead Generation**: Automate form submissions across multiple sites
- **Data Collection**: Extract product information, prices, reviews
- **Content Management**: Bulk upload content to multiple platforms
- **Testing**: Automated regression testing for web applications
- **Monitoring**: Regular health checks and status monitoring
- **Social Media**: Automated posting and engagement

---

**Built with ❤️ by [unnikrishnan077](https://github.com/unnikrishnan077)**

*Streamlit Web Automation System - Automate the web, amplify your productivity!*