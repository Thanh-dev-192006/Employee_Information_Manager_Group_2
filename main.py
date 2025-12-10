import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.models.manager.employee import EmployeeManager
from app.models.manager.department import DepartmentManager
from app.models.manager.project import ProjectManager
from app.models.manager.assignment import AssignmentManager
from app.models.manager.attendance import AttendanceManager
from app.models.manager.salary import SalaryManager
from app.models.manager.bonus_deduction import BonusDeductionManager
from app.models.manager.query import QueryManager
 

from app.ui.employee_screen import EmployeeScreen
from app.ui.department_screen import DepartmentScreen
from app.ui.project_screen import ProjectScreen
from app.ui.attendance_screen import AttendanceScreen
from app.ui.salary_screen import SalaryScreen
from app.ui.queries_screen import QueriesScreen
from app.ui.dashboard import Dashboard 

import mysql.connector
import random

class App(ttk.Window):
    def __init__(self):
        # Chọn theme ở đây ("litera", "cosmo", "flatly", "journal")
        super().__init__(themename="litera")

        style = ttk.Style()
        style.configure("Treeview", 
                        font=("Segoe UI", 11), 
                        rowheight=53)
        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 12, "bold"))

        self.title("Employee Information Manager - 161Corp")
        self.geometry("1280x800")

        

        # 7 managers
        self.managers = {
            "employee": EmployeeManager(),
            "department": DepartmentManager(),
            "project": ProjectManager(),
            "assignment": AssignmentManager(),
            "attendance": AttendanceManager(),
            "salary": SalaryManager(),
            "bonus_deduction": BonusDeductionManager(),
            "query": QueryManager(),
        }

        self._build_menu()
        self.container = ttk.Frame(self, padding=0)
        self.container.pack(fill="both", expand=True)

        self.screens = {}
        self._init_screens()

        self.show("dashboard")

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        def add(label, key):
            menubar.add_command(label=label, command=lambda: self.show(key))

        add("Dashboard", "dashboard")
        add("Employee", "employee")
        add("Department", "department")
        add("Project", "project")
        add("Attendance", "attendance")
        add("Salary", "salary")
        add("Queries", "queries")

    def _init_screens(self):
        
        
        self.screens["dashboard"] = Dashboard(self.container, self.managers) 


        self.screens["employee"] = EmployeeScreen(self.container, self.managers)
        self.screens["department"] = DepartmentScreen(self.container, self.managers)
        self.screens["project"] = ProjectScreen(self.container, self.managers)
        self.screens["attendance"] = AttendanceScreen(self.container, self.managers)
        self.screens["salary"] = SalaryScreen(self.container, self.managers)
        self.screens["queries"] = QueriesScreen(self.container, self.managers)

        for f in self.screens.values():
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show(self, key: str):
        screen = self.screens.get(key)
        if screen:
            screen.tkraise()
            if key == "dashboard" and hasattr(screen, "refresh_dashboard"):
                screen.refresh_dashboard()

if __name__ == "__main__":
    App().mainloop()