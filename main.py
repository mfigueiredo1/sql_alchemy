from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

# Create your Database
engine = create_engine('sqlite:///tasks.db', echo=False)
base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Define your Models
class User(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True) # Ensure email is unique
    tasks = relationship('Task', back_populates='user', cascade='all, delete-orphan')


class Task(base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='tasks')

base.metadata.create_all(engine)


# Utility Functions
def get_user_by_email(email):
    return session.query(User).filter_by(email=email).first()

def confirm_action(prompt:str) -> bool:
    return input(f"{prompt} (yes/no): ").strip().lower() == 'yes'


# CRUD Ops
def add_user():
    name,email = input("Enter user name: "), input("Enter the email: ")
    if get_user_by_email(email):
        print(f'User with email {email} already exists.')

    try:
        session.add(User(name=name, email=email))
        session.commit()
        print(f'User {name} added successfully.')
    except IntegrityError:
        session.rollback()
        print(f'Error')



def add_task():
    email = input("Enter the user's email to add tasks: ")
    user = get_user_by_email(email)
    if not user:
        print(f'User with email {email} not found.')
        return
    title, description = input ("Enter task title: "), input("Enter task description: ")
    session.add(Task(title=title, description=description, user=user))
    session.commit()
    print("Added to the database: {title}:{description}")


# Query
def query_users():
    for user in session.query(User).all():
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")

def query_tasks():
    email = input("Enter the email of the user to query tasks: ")
    user = session.query(User).filter_by(email=email).first()
    if not user:
        print(f'There was no user with that email')
        return

    for task in user.tasks:
        print(f"Task ID: {task.id}, Title: {task.title}")

def update_user():
    email = input("Enter the email of the user to update: ")
    user = get_user_by_email(email)
    if not user:
        print(f'User with email {email} not found.')
        return
    user.name = input(f"Enter new name for {user.name} (leave blank to keep current): ") or user.name
    new_email = input(f"Enter new email for {user.email} (leave blank to keep current): ") or user.email
    session.commit()  # Commit changes to the database
    print("User has been updated")

# Deleting
def delete_user():
    email = input("Enter the email of the user to delete: ")
    user = get_user_by_email(email)
    if not user:
       print("User with that email does not exist.")

    if confirm_action(f"Are you sure you want to delete: {user.name}?"):
        session.delete(user)
        session.commit()
        print(f"User {user.name} has been deleted.")

def delete_task():
    email = input("Enter the email of the user to delete a task from: ")
    user = get_user_by_email(email)

    for task in user.tasks:
        print(f"Task ID: {task.id}, Title: {task.title}")



    task_id = input("Enter the ID of the task to delete: ")

    task = next((t for t in user.tasks if str(t.id) == task_id), None) # MAking sure the tasks are associated with the user


    if confirm_action(f"Are you sure you want to delete task: {task.title}?"):
        session.delete(task)
        session.commit()
        print("Task has been deleted!")
# Main Ops

def main() -> None:
    actions = {
        "1": add_user,
        "2": add_task,
        "3": query_users,
        "4": query_tasks,
        "5": update_user,
        "6": delete_user,
        "7": delete_task,
    }

    while True:
        print("\nOptions:\n"
              "1. Add User\n2. Add Task\n3. Query Users\n4. Query Tasks\n"
              "5. Update User\n6. Delete User\n7. Delete Task\n8. Exit")
        choice = input("Enter an option: ")
        if choice == "8":
            print("Adios")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
    