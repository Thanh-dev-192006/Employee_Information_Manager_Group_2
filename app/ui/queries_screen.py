import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.ui.widgets import SortableTreeview

class QueriesScreen(ttk.Frame):
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.query_mgr = managers["query"]

        ttk.Label(self, text="QUERIES", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        top = ttk.Frame(self)
        top.pack(fill="x", pady=(10,6))

        self.q = tk.StringVar(value="query1")
        ttk.Radiobutton(top, text="Query 1 (INNER JOIN)", variable=self.q, value="query1").pack(side="left")
        ttk.Radiobutton(top, text="Query 2 (LEFT JOIN)", variable=self.q, value="query2").pack(side="left", padx=8)
        ttk.Radiobutton(top, text="Query 3 (Multi-table)", variable=self.q, value="query3").pack(side="left", padx=8)
        ttk.Radiobutton(top, text="Query 4 (Above Avg)", variable=self.q, value="query4").pack(side="left", padx=8)

        ttk.Button(top, text="Run", command=self.run).pack(side="right")
        ttk.Button(top, text="Export CSV", command=self.export_csv).pack(side="right", padx=6)

        self.search = tk.StringVar()
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0,6))
        ttk.Label(bar, text="Search filter:").pack(side="left")
        ttk.Entry(bar, textvariable=self.search, width=40).pack(side="left", padx=6)
        ttk.Button(bar, text="Apply", command=self.apply_filter).pack(side="left")

        self.tree = SortableTreeview(self, columns=(), show="headings", height=16)
        self.tree.pack(fill="both", expand=True)

        self._raw = []

    def _call(self):
        k = self.q.get()
        if k == "query1":
            return self.query_mgr.query_employee_project_roles()
        if k == "query2":
            return self.query_mgr.query_all_employees_with_roles()
        if k == "query3":
            return self.query_mgr.query_employee_project_manager()
        return self.query_mgr.query_above_average_salary()
        

  
    

    def run(self):
        try:
            self._raw = self._call()
            self.render(self._raw)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def render(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if not rows:
            self.tree["columns"] = ()
            return

        cols = list(rows[0].keys())
        self.tree["columns"] = cols
        special_widths = {
            "employee_id": 100,
            "full_name": 200,
            "email": 220,
            "project_name": 230,
            "department_name": 200,
            "position": 160,
            "base_salary": 115,
            "hours_worked": 110,
            "project_role": 150,
            "manager_email": 190
        }

        for c in cols:
            self.tree.heading(c, text=c)
            w = special_widths.get(c, 150)
            if "_id" in c or c == "id" or "total_assignments" in c: 
                anchor = "center"
            else: 
                anchor = "w"
            self.tree.column(c, width=w, anchor=anchor)
        self.tree.enable_sorting()

        for r in rows:
            row_values = []
            for c in cols:
                val = r.get(c, "")
                if c in ["base_salary", "overall_avg_base_salary", "difference", "budget"]:
                    try:
                        val = f"{float(val):,.0f}"
                    except (ValueError, TypeError):
                        pass
                
                row_values.append(val)

            self.tree.insert("", "end", values=row_values)

    def apply_filter(self):
        kw = self.search.get().strip().lower()
        if not kw:
            self.render(self._raw)
            return
        filtered = []
        for r in self._raw:
            text = " ".join(str(v) for v in r.values()).lower()
            if kw in text:
                filtered.append(r)
        self.render(filtered)

    def export_csv(self):
        if not self._raw:
            messagebox.showwarning("Missing", "No data to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path:
            return
        try:
            self.query_mgr.export_to_csv(self._raw, path)
            messagebox.showinfo("OK", f"Exported: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))