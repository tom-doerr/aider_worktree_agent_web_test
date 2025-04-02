import streamlit as st
from task_manager.db import TaskDB


def main():
    st.title("Task Manager")
    db = TaskDB()

    # Add task form
    with st.form("add_task"):
        task = st.text_input("New task")
        submitted = st.form_submit_button("Add")
        if submitted and task:
            db.add_task(task)

    # List tasks
    tasks = db.list_tasks()
    st.write("## Your Tasks")
    for task in tasks:
        st.write(f"- {task['description']}")


if __name__ == "__main__":
    main()
