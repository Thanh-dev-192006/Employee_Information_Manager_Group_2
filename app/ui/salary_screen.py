import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.ui.widgets import SortableTreeview
from app.dialogs.bonus_deduction_dialog import BonusDeductionDialog
from app.models.utils.helpers import to_vnd, format_currency_vnd
from app.models.utils.helpers import month_number_to_name

class SalaryScreen(ttk.Frame):
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.managers = managers
        self.sal_mgr = managers["salary"]

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="SALARY", font=("Segoe UI", 14, "bold")).pack(side="left")

        now = datetime.now()
        self.month = tk.IntVar(value=now.month)
        self.year = tk.IntVar(value=now.year)

        ttk.Label(top, text="Month:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.month, values=list(range(1,13)), state="readonly", width=5).pack(side="left")
        ttk.Label(top, text="Year:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.year, values=list(range(now.year-2, now.year+3)), state="readonly", width=7).pack(side="left")

        ttk.Button(top, text="Load", command=self.refresh).pack(side="left", padx=8)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(8, 0))

        # Load danh sách nhân viên
        self.emps = self.emp_mgr.get_all_employees(limit=1000, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}

        ttk.Label(action_bar, text="Employee:").pack(side="left")
        self.employee_id = tk.StringVar(value=(next(iter(self.emp_map.keys())) if self.emp_map else ""))
        ttk.Combobox(
            action_bar,
            textvariable=self.employee_id,
            values=list(self.emp_map.keys()),
            state="readonly",
            width=30
        ).pack(side="left", padx=(4, 12))



        ttk.Button(top, text="Auto Calculate Salary", command=self.on_calc).pack(side="right")
        ttk.Button(top, text="Add Bonus/Deduction", command=self.on_add_bd).pack(side="right", padx=6)

        cols = ("employee_id","employee_name","base_salary_vnd","total_bonus_vnd","total_deduction_vnd","net_amount_vnd")
        self.tree = SortableTreeview(self, columns=cols, show="headings", height=16)
        self.tree.pack(fill="both", expand=True, pady=(10,0))
        heads = {
            "employee_id":"ID","employee_name":"Full Name",
            "base_salary_vnd":"Base Salary","total_bonus_vnd":"Bonus",
            "total_deduction_vnd":"Deduction","net_salary_vnd":"Net Amount"
        }
        widths = {"employee_id":60,"employee_name":220,"base_salary_vnd":140,"total_bonus_vnd":120,"total_deduction_vnd":120,"net_salary_vnd":140}
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.enable_sorting()

        self.refresh()

    def _get_selected_emp_id(self):
        """ Lấy employee_id từ combobox"""
        return self.emp_map.get(self.employee_id.get())

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        month_name = month_number_to_name(int(self.month.get()))  
        try:
            rows = self.sal_mgr.get_salary_by_month(month_name, int(self.year.get()))
            for r in rows:
                self.tree.insert("", "end", values=(
                    r.get("employee_id"),
                    r.get("employee_name"),
                    format_currency_vnd(to_vnd(r.get("base_salary"))),
                    format_currency_vnd(to_vnd(r.get("total_bonus"))),
                    format_currency_vnd(to_vnd(r.get("total_deduction"))),
                    format_currency_vnd(to_vnd(r.get("net_amount"))),
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_calc(self):
        emp_id = self._get_selected_emp_id()
        if not emp_id:
            messagebox.showwarning("Missing", "Please select an employee")
            return

        month_name = month_number_to_name(int(self.month.get()))
        try:
            res = self.sal_mgr.calculate_salary(emp_id, month_name, int(self.year.get()))
            messagebox.showinfo("OK", res.get("message","Salary calculated"))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_add_bd(self):
        dlg = BonusDeductionDialog(self, self.managers)
        self.wait_window(dlg)
        self.refresh()