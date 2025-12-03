import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.ui.widgets import SortableTreeview
from app.dialogs.attendance_dialog import AttendanceDialog
from app.models.utils.helpers import format_display_date, format_display_time

class AttendanceScreen(ttk.Frame):
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.managers = managers
        self.emp_mgr = managers["employee"]
        self.att_mgr = managers["attendance"]

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="CHẤM CÔNG", font=("Segoe UI", 14, "bold")).pack(side="left")

        self.emps = self.emp_mgr.get_all_employees(limit=1000, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}

        self.emp_choice = tk.StringVar(value=(next(iter(self.emp_map.keys())) if self.emp_map else ""))
        ttk.Label(top, text="Nhân viên:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.emp_choice, values=list(self.emp_map.keys()), state="readonly", width=28)\
            .pack(side="left")

        now = datetime.now()
        self.month = tk.IntVar(value=now.month)
        self.year = tk.IntVar(value=now.year)

        ttk.Label(top, text="Tháng:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.month, values=list(range(1,13)), state="readonly", width=5).pack(side="left")
        ttk.Label(top, text="Năm:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.year, values=list(range(now.year-2, now.year+3)), state="readonly", width=7).pack(side="left")

        ttk.Button(top, text="Tải", command=self.refresh).pack(side="left", padx=8)
        ttk.Button(top, text="Mark", command=self.on_mark).pack(side="right")

        self.stats = ttk.Label(self, text="Thống kê: -")
        self.stats.pack(anchor="w", pady=(8,4))

        cols = ("work_date","weekday","check_in","check_out","status")
        self.tree = SortableTreeview(self, columns=cols, show="headings", height=16)
        self.tree.pack(fill="both", expand=True)
        for c,t,w in [
            ("work_date","Ngày",120),
            ("weekday","Thứ",80),
            ("check_in","Check-in",100),
            ("check_out","Check-out",100),
            ("status","Trạng thái",120),
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.enable_sorting()

        self.refresh()

    def _emp_id(self):
        return self.emp_map.get(self.emp_choice.get())

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        emp_id = self._emp_id()
        if not emp_id:
            return
        try:
            rows = self.att_mgr.get_attendance_by_employee(emp_id, int(self.month.get()), int(self.year.get()))
            present = sum(1 for r in rows if r.get("status") == "Present")
            total = len(rows)
            rate = (present/total*100.0) if total else 0.0
            self.stats.config(text=f"Thống kê: {present}/{total} ngày đi làm - Tỷ lệ: {rate:.1f}%")

            for r in rows:
                d = r.get("work_date")
                weekday = d.strftime("%A") if d else ""
                self.tree.insert("", "end", values=(
                    format_display_date(d),
                    weekday,
                    format_display_time(r.get("check_in")),
                    format_display_time(r.get("check_out")),
                    r.get("status")
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_mark(self):
        emp_id = self._emp_id()
        if not emp_id:
            messagebox.showwarning("Thiếu", "Chọn nhân viên")
            return
        dlg = AttendanceDialog(self, self.att_mgr, employee_id=emp_id)
        self.wait_window(dlg)
        self.refresh()