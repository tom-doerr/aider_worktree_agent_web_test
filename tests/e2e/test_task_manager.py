import pytest
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from unittest.mock import MagicMock, patch

# Add project root to path so tests can find task_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from task_manager.db import TaskDB
from task_manager.app import main

@pytest.fixture(scope="module", name="task_db")
def fixture_task_db():
    """Fixture providing database connection"""
    try:
        db = TaskDB()
        yield db
        db.close()
    except RuntimeError as e:
        pytest.skip(f"Skipping test - database not available: {str(e)}")


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


def test_db_connection_failure(monkeypatch):
    """Test database connection failure handling"""
    monkeypatch.setenv("DB_HOST", "invalid_host")
    with pytest.raises(RuntimeError):
        TaskDB(max_retries=1, retry_delay=0)

def test_db_schema(task_db):
    """Test database schema exists and is correct"""
    with task_db.conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tasks'
        """)
        columns = {row[0]: row[1] for row in cur.fetchall()}
        
    assert "id" in columns
    assert columns["id"] in ("integer", "bigint")
    assert "description" in columns
    assert columns["description"] == "text"




@patch("streamlit.title")
@patch("streamlit.text_input")
@patch("streamlit.form_submit_button")
@patch("streamlit.write")
def test_app_main(mock_write, mock_submit, mock_input, mock_title):
    """Test the main app function"""
    mock_db = MagicMock()
    mock_db.list_tasks.return_value = [{"id": 1, "description": "Test task"}]
    mock_input.return_value = "Test task"
    mock_submit.return_value = True

    with patch("task_manager.app.TaskDB", return_value=mock_db):
        main()

    mock_title.assert_called_once_with("Task Manager")
    mock_db.add_task.assert_called_once_with("Test task")
    mock_db.list_tasks.assert_called_once()


@pytest.fixture(scope="module")
def streamlit_app():
    """Fixture to start Streamlit app in background"""
    import subprocess
    import time
    
    process = subprocess.Popen([
        "streamlit", "run", 
        str(Path(__file__).parent.parent.parent / "task_manager" / "app.py"),
        "--server.port=8501",
        "--server.headless=true"
    ])
    time.sleep(2)  # Give app time to start
    yield
    process.terminate()

def test_streamlit_interface(streamlit_app):
    """Test the Streamlit UI with Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("http://localhost:8501")
        
        # Test basic UI elements
        expect(page.get_by_role("heading", name="Task Manager")).to_be_visible()
        expect(page.get_by_label("New task")).to_be_visible()
        expect(page.get_by_role("button", name="Add")).to_be_visible()

        # Test adding a task
        test_task = "Test task from UI"
        page.get_by_label("New task").fill(test_task)
        page.get_by_role("button", name="Add").click()
        
        # Verify task appears
        expect(page.get_by_text(test_task)).to_be_visible()
        
        browser.close()
