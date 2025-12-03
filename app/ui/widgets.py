import tkinter as tk
from tkinter import ttk

class SortableTreeview(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._sort_desc = {}

    def enable_sorting(self):
        for col in self["columns"]:
            self.heading(col, command=lambda c=col: self._sort_by(c))

    def _sort_by(self, col):
        items = [(self.set(k, col), k) for k in self.get_children("")]
        desc = self._sort_desc.get(col, False)

        def _key(x):
            v = x[0]
            try:
                return float(v.replace(",", ""))
            except Exception:
                return v.lower() if isinstance(v, str) else v

        items.sort(key=_key, reverse=desc)
        for idx, (_, k) in enumerate(items):
            self.move(k, "", idx)

        self._sort_desc[col] = not desc

class PaginationBar(ttk.Frame):
    def __init__(self, master, on_prev, on_next):
        super().__init__(master)
        self.on_prev = on_prev
        self.on_next = on_next

        self.btn_prev = ttk.Button(self, text="◀ Prev", command=self.on_prev)
        self.btn_next = ttk.Button(self, text="Next ▶", command=self.on_next)
        self.lbl = ttk.Label(self, text="Page 1")

        self.btn_prev.pack(side="left")
        self.lbl.pack(side="left", padx=10)
        self.btn_next.pack(side="left")

    def set_page(self, page_idx: int):
        self.lbl.config(text=f"Page {page_idx + 1}")