import tkinter as tk
from tkinter import ttk, messagebox

from app.ui.widgets import SortableTreeview, PaginationBar
from app.dialogs.employee_dialog import EmployeeDialog
from app.utils.ui_helpers import to_vnd, format_currency_vnd

class EmployeeScreen(ttk.Frame):
    PAGE_SIZE = 20

    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.managers = managers
        self.emp_mgr = managers["employee"]

        self.page = 0
        self.search_mode = False
        self.search_keyword = ""

        header = ttk.Frame(self)
        header.pack(fill="x")

        ttk.Label(header, text="NHÂN VIÊN", font=("Segoe UI", 14, "bold")).pack(side="left")

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(10, 6))

        self.kw = tk.StringVar()
        ttk.Label(actions, text="Tìm:").pack(side="left")
        ttk.Entry(actions, textvariable=self.kw, width=30).pack(side="left", padx=6)
        ttk.Button(actions, text="Tìm kiếm", command=self.on_search).pack(side="left")
        ttk.Button(actions, text="Clear", command=self.on_clear).pack(side="left", padx=6)

        ttk.Button(actions, text="Thêm", command=self.on_add).pack(side="right")
        ttk.Button(actions, text="Sửa", command=self.on_edit).pack(side="right", padx=6)
        ttk.Button(actions, text="Xóa", command=self.on_delete).pack(side="right")

        cols = ("employee_id","full_name","gender","phone_number","email","department_name","position","base_salary_vnd")
        self.tree = SortableTreeview(self, columns=cols, show="headings", height=18)
        self.tree.pack(fill="both", expand=True)

        headings = {
            "employee_id": "ID",
            "full_name": "Họ tên",
            "gender": "Giới tính",
            "phone_number": "SĐT",
            "email": "Email",
            "department_name": "Phòng ban",
            "position": "Chức vụ",
            "base_salary_vnd": "Lương",
        }
        widths = {"employee_id":60,"full_name":200,"gender":80,"phone_number":120,"email":200,"department_name":140,"position":140,"base_salary_vnd":120}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")

        self.tree.enable_sorting()

        self.pager = PaginationBar(self, self.prev_page, self.next_page)
        self.pager.pack(fill="x", pady=(6,0))

        self.refresh()

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        return {"employee_id": int(values[0])}

    def refresh(self):
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)

            if self.search_mode and self.search_keyword.strip():
                rows = self.emp_mgr.search_employees(self.search_keyword.strip())
                self.pager.set_page(0)
            else:
                rows = self.emp_mgr.get_all_employees(limit=self.PAGE_SIZE, offset=self.page*self.PAGE_SIZE)
                self.pager.set_page(self.page)

            for r in rows:
                salary_vnd = format_currency_vnd(to_vnd(r.get("base_salary")))
                self.tree.insert("", "end", values=(
                    r.get("employee_id"),
                    r.get("full_name"),
                    r.get("gender"),
                    r.get("phone_number"),
                    r.get("email"),
                    r.get("department_name"),
                    r.get("position"),
                    salary_vnd
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được nhân viên: {e}")

    def on_search(self):
        self.search_keyword = self.kw.get()
        self.search_mode = True
        self.page = 0
        self.refresh()

    def on_clear(self):
        self.kw.set("")
        self.search_mode = False
        self.search_keyword = ""
        self.page = 0
        self.refresh()

    def on_add(self):
        dlg = EmployeeDialog(self, self.managers, mode="create")
        self.wait_window(dlg)
        self.refresh()

    def on_edit(self):
        sel = self._selected()
        if not sel:
            messagebox.showwarning("Thiếu", "Chọn 1 nhân viên để sửa")
            return
        try:
            emp = self.emp_mgr.get_employee_by_id(sel["employee_id"])
            dlg = EmployeeDialog(self, self.managers, mode="edit", employee=emp)
            self.wait_window(dlg)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete(self):
        sel = self._selected()
        if not sel:
            messagebox.showwarning("Thiếu", "Chọn 1 nhân viên để xóa")
            return
        if not messagebox.askyesno("Xác nhận", "Xóa nhân viên này?"):
            return
        try:
            res = self.emp_mgr.delete_employee(sel["employee_id"])
            messagebox.showinfo("OK", res.get("message","Đã xóa"))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def prev_page(self):
        if self.search_mode:
            return
        if self.page > 0:
            self.page -= 1
            self.refresh()

    def next_page(self):
        if self.search_mode:
            return
        self.page += 1
        self.refresh()