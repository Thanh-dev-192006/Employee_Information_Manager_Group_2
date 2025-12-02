import tkinter as tk
from tkinter import ttk, messagebox

from app.ui.widgets import SortableTreeview
from app.dialogs.project_dialog import ProjectDialog
from app.dialogs.assignment_dialog import AssignmentDialog
from app.utils.ui_helpers import to_vnd, format_currency_vnd, format_display_date

class ProjectScreen(ttk.Frame):
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.managers = managers
        self.proj_mgr = managers["project"]
        self.assign_mgr = managers["assignment"]

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="DỰ ÁN", font=("Segoe UI", 14, "bold")).pack(side="left")

        self.status = tk.StringVar(value="all")
        ttk.Label(top, text="Filter:").pack(side="left", padx=(16,4))
        ttk.Combobox(top, textvariable=self.status, values=["all","ongoing","completed"], state="readonly", width=12)\
            .pack(side="left")
        ttk.Button(top, text="Apply", command=self.refresh).pack(side="left", padx=6)

        ttk.Button(top, text="Phân công nhân viên", command=self.on_assign).pack(side="right")
        ttk.Button(top, text="Xóa", command=self.on_delete).pack(side="right", padx=6)
        ttk.Button(top, text="Sửa", command=self.on_edit).pack(side="right", padx=6)
        ttk.Button(top, text="Thêm", command=self.on_add).pack(side="right")

        cols = ("project_id","project_name","start_date","end_date","budget_vnd","status","department_name","total_employees","total_hours_worked")
        self.tree = SortableTreeview(self, columns=cols, show="headings", height=16)
        self.tree.pack(fill="both", expand=True, pady=(10,0))

        heads = {
            "project_id":"ID","project_name":"Tên dự án","start_date":"Bắt đầu","end_date":"Kết thúc",
            "budget_vnd":"Ngân sách","status":"Trạng thái","department_name":"Phòng ban",
            "total_employees":"Số NV","total_hours_worked":"Giờ"
        }
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=120, anchor="w")
        self.tree.column("project_id", width=60)
        self.tree.column("project_name", width=220)
        self.tree.enable_sorting()

        self.refresh()

    def _selected_project(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        return int(vals[0])

    def refresh(self):
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)

            s = self.status.get()
            status = None if s=="all" else s
            rows = self.proj_mgr.get_all_projects(status=status)

            for r in rows:
                start = format_display_date(r.get("start_date"))
                end = format_display_date(r.get("end_date")) if r.get("end_date") else ""
                budget = format_currency_vnd(to_vnd(r.get("budget")))
                st = "Đang thực hiện" if (r.get("end_date") is None) else "Hoàn thành"
                self.tree.insert("", "end", values=(
                    r.get("project_id"),
                    r.get("project_name"),
                    start,
                    end,
                    budget,
                    st,
                    r.get("department_name"),
                    r.get("total_employees") or 0,
                    r.get("total_hours_worked") or 0
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_add(self):
        dlg = ProjectDialog(self, self.managers, mode="create")
        self.wait_window(dlg)
        self.refresh()

    def on_edit(self):
        pid = self._selected_project()
        if not pid:
            messagebox.showwarning("Thiếu", "Chọn 1 dự án để sửa")
            return
        try:
            proj = next(p for p in self.proj_mgr.get_all_projects(None) if int(p["project_id"]) == pid)
            dlg = ProjectDialog(self, self.managers, mode="edit", project=proj)
            self.wait_window(dlg)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete(self):
        pid = self._selected_project()
        if not pid:
            messagebox.showwarning("Thiếu", "Chọn 1 dự án để xóa")
            return
        if not messagebox.askyesno("Xác nhận", "Xóa dự án này?"):
            return
        try:
            res = self.proj_mgr.delete_project(pid)
            messagebox.showinfo("OK", res.get("message","Đã xóa"))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_assign(self):
        pid = self._selected_project()
        if not pid:
            messagebox.showwarning("Thiếu", "Chọn 1 dự án để phân công")
            return
        dlg = AssignmentDialog(self, self.managers, project_id=pid)
        self.wait_window(dlg)
        self.refresh()