import psycopg2
import os
import time
from psycopg2 import OperationalError


class TaskDB:
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.conn = self._connect_with_retry()

    def _connect_with_retry(self):
        """Connect to PostgreSQL with retry logic and initialize schema"""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                conn = psycopg2.connect(
                    dbname=os.getenv("POSTGRES_DB", "tasks"),
                    user=os.getenv("POSTGRES_USER", "postgres"),
                    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                    host=os.getenv("DB_HOST", "localhost"),
                    port=os.getenv("DB_PORT", "5432"),
                )
                # Initialize schema if needed
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            description TEXT NOT NULL
                        )
                    """)
                    conn.commit()
                return conn
            except OperationalError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        raise RuntimeError(
            f"Failed to connect to database after {self.max_retries} attempts"
        ) from last_error

    def add_task(self, description):
        """Add a new task to the database"""
        if not description:
            raise ValueError("Task description cannot be empty")

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (description) VALUES (%s) RETURNING id",
                    (description,),
                )
                task_id = cur.fetchone()[0]
                self.conn.commit()
                return task_id
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to add task: {str(e)}") from e

    def list_tasks(self):
        """List all tasks from database"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, description FROM tasks ORDER BY id")
                return [{"id": row[0], "description": row[1]} for row in cur.fetchall()]
        except Exception as e:
            raise RuntimeError(f"Failed to list tasks: {str(e)}") from e

    def delete_all_tasks(self):
        """Delete all tasks from database"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM tasks")
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to delete tasks: {str(e)}") from e

    def delete_task(self, task_id):
        """Delete a specific task from database"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to delete task: {str(e)}") from e

    def close(self):
        self.conn.close()
