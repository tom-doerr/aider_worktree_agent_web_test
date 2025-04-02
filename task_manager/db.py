import psycopg2
import os
import time
from psycopg2 import OperationalError


class TaskDB:
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.conn = self._connect_with_retry()

    def _connect_with_retry(self):
        """Connect to PostgreSQL with retry logic"""
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
                return conn
            except OperationalError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        raise RuntimeError(
            f"Failed to connect to database after {self.max_retries} attempts"
        ) from last_error

    def add_task(self, description):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (description) VALUES (%s)", (description,))
            self.conn.commit()

    def list_tasks(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, description FROM tasks")
            return [{"id": row[0], "description": row[1]} for row in cur.fetchall()]

    def delete_all_tasks(self):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM tasks")
            self.conn.commit()

    def close(self):
        self.conn.close()
