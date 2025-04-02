import pytest
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add project root to path so tests can find task_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from task_manager.db import TaskDB
except ImportError:
    from task_manager.db import TaskDB  # Second attempt if first fails


@pytest.fixture(scope="module", name="task_db")
def fixture_task_db():
    """Fixture providing database connection"""
    db = TaskDB()
    yield db
    db.close()


def test_add_and_list_tasks(task_db):
    """Test adding and listing tasks"""
    # Clear any existing tasks
    task_db.delete_all_tasks()

    # Add test task
    task_db.add_task("Test task 1")

    # Verify task exists
    tasks = task_db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Test task 1"

    # Test empty case
    task_db.delete_all_tasks()
    assert len(task_db.list_tasks()) == 0


def test_db_connection(task_db):
    """Test database connection is working"""
    assert task_db.conn is not None
    assert not task_db.conn.closed

def test_streamlit_interface():
    """Test the Streamlit UI with Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Start Streamlit app (assuming it runs on port 8501)
        page.goto("http://localhost:8501")

        # Test basic UI elements
        assert "Task Manager" in page.inner_text("h1")
        assert "New task" in page.inner_text("label")
        assert "Add" in page.inner_text("button")

        # Test adding a task
        page.fill("input", "Test task from UI")
        page.click("button:has-text('Add')")
        
        # Verify task appears
        page.wait_for_selector("text=Test task from UI")
        
        browser.close()
