import psycopg2


class TaskDB:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname="tasks", user="postgres", password="postgres", host="localhost"
            )
        except psycopg2.OperationalError as e:
            raise RuntimeError("Failed to connect to database") from e

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
