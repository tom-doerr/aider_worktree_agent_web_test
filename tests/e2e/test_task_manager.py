import pytest
from playwright.sync_api import sync_playwright
from task_manager.db import TaskDB

@pytest.fixture(scope="module")
def db():
    """Fixture providing database connection"""
    db = TaskDB()
    yield db
    db.close()

def test_add_and_list_tasks(db):
    """Test adding and listing tasks"""
    # Clear any existing tasks
    db.delete_all_tasks()
    
    # Add test task
    db.add_task("Test task 1")
    
    # Verify task exists
    tasks = db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Test task 1"

def test_streamlit_interface():
    """Test the Streamlit UI with Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Start Streamlit app (assuming it runs on port 8501)
        page.goto("http://localhost:8501")
        
        # Test basic UI elements
        assert "Task Manager" in page.inner_text("h1")
        
        browser.close()
