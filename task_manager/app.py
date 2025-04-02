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
                st.write(f"- {task['description']}")
    except (RuntimeError, psycopg2.Error) as e:
        st.error(f"Error loading tasks: {str(e)}")


if __name__ == "__main__":
    main()
