from datetime import datetime as dt
from datetime import timedelta
from DbTool import DbTool


class Menu:
    n_menus = 0
    db = DbTool("todo.db")
    menu = """
1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks
5) Add task
6) Delete task
0) Exit
""".strip()

    def __new__(cls):
        if cls.n_menus == 0:
            cls.n_menus += 1
            return object.__new__(cls)

    @staticmethod
    def print_tasks(tasks, message, print_date=False):
        """
        Print a list of tasks

        :param list tasks: result of a database query
        :param str message: message to print if out of tasks
        :param bool print_date: to print date of the task or not
        """
        if not tasks:
            print(message)
            return

        if print_date:
            for i, task in enumerate(tasks):
                print(f"{i+1}. {task.task}. {task.deadline.strftime('%d %b')}")
        else:
            for i, task in enumerate(tasks):
                print(f"{i+1}. {task.task}")

        print()

    def print_menu(self):
        """
        Prints To-Do list menu
        """
        print(self.menu)

    def show_tasks_for_period(self, message, since=dt.today().date(), days=8):
        """
        Get tasks from database and print them for a specified period

        :param str message: message to print if out of tasks
        :param datetime.date since: day to print since
        :param int days: period for printing
        """
        day = since
        for _ in range(days):
            rows = (
                self.db.session.query(self.db.Task)
                .filter(self.db.Task.deadline == day)
                .all()
            )
            date = day.strftime("%A %d %b") + ":"
            print("\n" + date)
            self.print_tasks(rows, message)
            day += timedelta(days=1)

    def get_timetable(self, kind="Today"):
        """
        Get tasks from database and print them

        :param str kind: keyword specifying printing result
        """
        rows = None
        message, message_empty = "", "Nothing to do!"
        print_date = False
        if kind == "Week":
            self.show_tasks_for_period(days=8, message=message_empty)
            return

        elif kind == "Today":
            today_day = dt.today().date()
            rows = (
                self.db.session.query(self.db.Task)
                .filter(self.db.Task.deadline == today_day)
                .all()
            )
            message = "Today " + today_day.strftime("%d %b") + ":"

        elif kind == "All":
            rows = self.db.session.query(self.db.Task).all()
            message = "All tasks:"
            print_date = True

        elif kind == "Missed":
            today_day = dt.today().date()
            rows = (
                self.db.session.query(self.db.Task)
                .filter(self.db.Task.deadline < today_day)
                .order_by(self.db.Task.deadline)
                .all()
            )
            message = "Missed tasks:"
            message_empty = "Nothing is missed!"
            print_date = True

        print(message)
        self.print_tasks(rows, message=message_empty, print_date=print_date)

    def add_task(self, task, deadline):
        """
        Add new task to database

        :param str task: the task to add
        :param datetime.date deadline: deadline for the task
        """
        new_row = self.db.Task(task=task, deadline=deadline)
        self.db.session.add(new_row)
        self.db.session.commit()

    def delete_task(self, task_ind):
        """
        Delete task from database

        :param int task_ind: index of the task in the list of tasks to delete
        """
        task_to_delete = self.db.session.query(self.db.Task).all()[task_ind - 1]
        self.db.session.delete(task_to_delete)
        self.db.session.commit()

    def run(self):
        """
        Run printing menu and input processing
        """
        periods = {1: "Today", 2: "Week", 3: "All", 4: "Missed"}
        while True:
            self.print_menu()
            action = int(input())
            if action in [1, 2, 3, 4]:
                self.get_timetable(periods[action])

            elif action == 5:
                task = input("\nEnter task\n")
                deadline = dt.strptime(input("Enter deadline\n"), "%Y-%m-%d")
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
                print("Entered command is not defined!")
                break


if __name__ == "__main__":
    menu = Menu()
    menu.run()
