from datetime import datetime, timedelta

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


class Menu:
    n_menus = 0

    def __new__(cls, engine):
        if cls.n_menus == 0:
            cls.n_menus += 1
            return object.__new__(cls)

    def __init__(self, engine):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    @staticmethod
    def print_menu():
        print(f"1) Today's tasks\n"
              "2) Week's tasks\n"
              "3) All tasks\n"
              "4) Missed tasks\n"
              "5) Add task\n"
              "6) Delete task\n"
              "0) Exit")

    @staticmethod
    def print_tasks(tasks, message, print_date=False):
        if not tasks:
            print(message)
            return

        if print_date:
            for i, task in enumerate(tasks):
                print(f"{i + 1}. {task.task}. {task.deadline.strftime('%d %b')}")
        else:
            for i, task in enumerate(tasks):
                print(f"{i + 1}. {task.task}")

        print()

    def show_tasks_for_period(self, message, since=datetime.today().date(), days=8):
        day = since
        for _ in range(days):
            rows = self.session \
                .query(Table) \
                .filter(Table.deadline == day) \
                .all()
            date = day.strftime("%A %d %b") + ":"
            print("\n" + date)
            self.print_tasks(rows, message)
            day += timedelta(days=1)

    def get_timetable(self, kind="Today"):
        rows = None
        message, message_empty = '', 'Nothing to do!'
        print_date = False
        if kind == "Week":
            self.show_tasks_for_period(days=8, message=message_empty)
            return

        elif kind == "Today":
            today_day = datetime.today().date()
            rows = self.session \
                       .query(Table) \
                       .filter(Table.deadline == today_day) \
                       .all()
            message = "Today " + today_day.strftime("%d %b") + ":"

        elif kind == "All":
            rows = self.session.query(Table).all()
            message = "All tasks:"
            print_date = True

        elif kind == "Missed":
            today_day = datetime.today().date()
            rows = self.session \
                       .query(Table) \
                       .filter(Table.deadline < today_day) \
                       .order_by(Table.deadline) \
                       .all()
            message = "Missed tasks:"
            message_empty = "Nothing is missed!"
            print_date = True

        print(message)
        self.print_tasks(rows, message=message_empty, print_date=print_date)

    def add_task(self, task, deadline):
        new_row = Table(task=task, deadline=deadline)
        self.session.add(new_row)
        self.session.commit()

    def delete_task(self, task_ind):
        task_to_delete = self.session.query(Table).all()[task_ind - 1]
        self.session.delete(task_to_delete)
        self.session.commit()

    def run(self):
        periods = {1: "Today", 2: "Week", 3: "All", 4: "Missed"}
        while True:
            self.print_menu()
            action = int(input())
            if action in [1, 2, 3, 4]:
                self.get_timetable(periods[action])

            elif action == 5:
                print("\nEnter task")
                task = input()
                print("Enter deadline")
                deadline = datetime.strptime(input(), "%Y-%m-%d")
                self.add_task(task, deadline)
                print("The task has been added!\n")

            elif action == 6:
                print("\nChose the number of the task you want to delete:")
                self.get_timetable(periods[3])
                task_id = int(input())
                self.delete_task(task_id)
                print("The task has been deleted!\n")

            elif action == 0:
                print("Bye!")
                break

            else:
                break


engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base.metadata.create_all(engine)

menu = Menu(engine)
menu.run()
