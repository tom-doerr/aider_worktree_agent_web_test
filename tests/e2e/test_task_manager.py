import pytest
import sys
import os
from playwright.sync_api import sync_playwright

# Add project root to path so tests can find task_manager
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from task_manager.db import TaskDB


@pytest.fixture(scope="module")
def db_connection():
    """Fixture providing database connection"""
    db = TaskDB()
    yield db
    db.close()


def test_add_and_list_tasks(db_connection):
    """Test adding and listing tasks"""
    # Clear any existing tasks
    task_db.delete_all_tasks()

    # Add test task
    task_db.add_task("Test task 1")

    # Verify task exists
    tasks = task_db.list_tasks()
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
