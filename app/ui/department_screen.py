import tkinter as tk
from tkinter import ttk, messagebox

from app.ui.widgets import SortableTreeview
from app.dialogs.department_dialog import DepartmentDialog

class DepartmentScreen(ttk.Frame):
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.managers = managers
        self.dept_mgr = managers["department"]
        self.emp_mgr = managers["employee"]

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Label(top, text="DEPARTMENT", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Add", command=self.on_add).pack(side="right")
        ttk.Button(top, text="Edit", command=self.on_edit).pack(side="right", padx=6)
        ttk.Button(top, text="Delete", command=self.on_delete).pack(side="right")

        main = ttk.PanedWindow(self, orient="horizontal")
        main.pack(fill="both", expand=True, pady=(10,0))

        left = ttk.Frame(main)
        right = ttk.Frame(main)
        main.add(left, weight=1)
        main.add(right, weight=2)

        ttk.Label(left, text="Department List").pack(anchor="w")
        self.dept_tree = SortableTreeview(left, columns=("department_id","department_name","location","employee_count"), show="headings", height=16)
        self.dept_tree.pack(fill="both", expand=True, pady=(4,0))
        for c,t,w in [
            ("department_id","ID",60),
            ("department_name","Department Name",160),
            ("location","Location",140),
            ("employee_count","Employees",80),
        ]:
            self.dept_tree.heading(c, text=t)
            self.dept_tree.column(c, width=w, anchor="w")
        self.dept_tree.enable_sorting()
        self.dept_tree.bind("<<TreeviewSelect>>", lambda e: self.show_employees())

        ttk.Label(right, text="Employees in Department (click department on left)").pack(anchor="w")
        self.emp_tree = SortableTreeview(right, columns=("employee_id","full_name","position","email"), show="headings", height=16)
        self.emp_tree.pack(fill="both", expand=True, pady=(4,0))
        for c,t,w in [
            ("employee_id","ID",60),
            ("full_name","Full Name",200),
            ("position","Position",160),
            ("email","Email",240),
        ]:
            self.emp_tree.heading(c, text=t)
            self.emp_tree.column(c, width=w, anchor="w")
        self.emp_tree.enable_sorting()

        self.refresh()

    def refresh(self):
        try:
            for i in self.dept_tree.get_children():
                self.dept_tree.delete(i)
            depts = self.dept_mgr.get_all_departments()
            for d in depts:
                self.dept_tree.insert("", "end", values=(
                    d.get("department_id"),
                    d.get("department_name"),
                    d.get("location"),
                    d.get("employee_count") or 0
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _selected_dept_id(self):
        sel = self.dept_tree.selection()
        if not sel:
            return None
        return int(self.dept_tree.item(sel[0], "values")[0])

    def show_employees(self):
        for i in self.emp_tree.get_children():
            self.emp_tree.delete(i)

        dept_id = self._selected_dept_id()
        if not dept_id:
            return
        try:
            # backend không có get_employees_by_department => lấy nhiều rồi filter (dataset nhóm thường nhỏ)
            emps = self.emp_mgr.get_all_employees(limit=10000, offset=0)
            emps = [e for e in emps if int(e.get("department_id")) == dept_id]
            for e in emps:
                self.emp_tree.insert("", "end", values=(
                    e.get("employee_id"),
                    e.get("full_name"),
                    e.get("position"),
                    e.get("email")
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_add(self):
        dlg = DepartmentDialog(self, self.dept_mgr, mode="create")
        self.wait_window(dlg)
        self.refresh()

    def on_edit(self):
        dept_id = self._selected_dept_id()
        if not dept_id:
            messagebox.showwarning("Missing", "Select a department to edit")
            return
        try:
            # dept_mgr không có get_by_id => lấy list rồi tìm
            dept = next((d for d in self.dept_mgr.get_all_departments() if int(d["department_id"]) == dept_id), None)
            if not dept:
                messagebox.showerror("Error", "Department not found")
                return
            dlg = DepartmentDialog(self, self.dept_mgr, mode="edit", dept=dept)
            self.wait_window(dlg)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_delete(self):
        dept_id = self._selected_dept_id()
        if not dept_id:
            messagebox.showwarning("Missing", "Select a department to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete this department?"):
            return
        try:
            res = self.dept_mgr.delete_department(dept_id)
            messagebox.showinfo("OK", res.get("message","Deleted"))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))