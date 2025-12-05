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
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160, anchor="w")
        self.tree.enable_sorting()

        for r in rows:
            self.tree.insert("", "end", values=[r.get(c,"") for c in cols])

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