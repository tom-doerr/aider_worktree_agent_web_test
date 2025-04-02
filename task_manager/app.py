import streamlit as st
import psycopg2
from task_manager.db import TaskDB


def main():
    st.title("Task Manager")
    db = TaskDB()

    # Add task form
    with st.form("add_task"):
        task = st.text_input("New task", placeholder="Enter task description...")
        submitted = st.form_submit_button("Add")
        if submitted:
            if not task:
                st.error("Please enter a task description")
            else:
                try:
                    db.add_task(task)
                    st.success("Task added successfully!")
                except (RuntimeError, psycopg2.Error) as e:
                    st.error(f"Error adding task: {str(e)}")

    # List tasks
    st.write("## Your Tasks")
    try:
        tasks = db.list_tasks()
        if not tasks:
            st.info("No tasks yet. Add one above!")
        else:
            for task in tasks:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"- {task['description']}")
                with col2:
                    if st.button("Delete", key=f"delete_{task['id']}"):
                        try:
                            with db.conn.cursor() as cur:
                                cur.execute("DELETE FROM tasks WHERE id = %s", (task['id'],))
                                db.conn.commit()
                            st.experimental_rerun()
                        except (RuntimeError, psycopg2.Error) as e:
                            st.error(f"Error deleting task: {str(e)}")
    except (RuntimeError, psycopg2.Error) as e:
        st.error(f"Error loading tasks: {str(e)}")


if __name__ == "__main__":
    main()
