import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from app.models.utils.helpers import parse_display_date, parse_display_time, format_display_date

class AttendanceDialog(tk.Toplevel):
    def __init__(self, master, att_mgr, employee_id: int):
        super().__init__(master)
        self.title("Chấm công")
        self.resizable(False, False)

        self.att_mgr = att_mgr
        self.employee_id = employee_id

        self.work_date = tk.StringVar(value=format_display_date(date.today()))
        self.check_in = tk.StringVar()
        self.check_out = tk.StringVar()
        self.status = tk.StringVar(value="Present")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Ngày (DD/MM/YYYY)").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.work_date).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Check-in (HH:MM, có thể trống)").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.check_in).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Check-out (HH:MM, có thể trống)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.check_out).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Trạng thái").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(body, textvariable=self.status, values=["Present","Absent","On Leave"], state="readonly")\
            .grid(row=3, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(body)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Hủy", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Lưu", command=self.on_save).pack(side="right")

        body.columnconfigure(1, weight=1)
        self.grab_set()
        self.transient(master)

    def on_save(self):
        try:
            d = parse_display_date(self.work_date.get())
            ci = self.check_in.get().strip()
            co = self.check_out.get().strip()
            ci_t = parse_display_time(ci) if ci else None
            co_t = parse_display_time(co) if co else None

            res = self.att_mgr.mark_attendance(self.employee_id, d, ci_t, co_t, self.status.get())
            messagebox.showinfo("OK", res.get("message","OK"))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))