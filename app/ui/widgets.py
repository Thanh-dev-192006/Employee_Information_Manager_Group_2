import tkinter as tk
from tkinter import ttk

class SortableTreeview(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._sort_desc = {}
        
        # --- CẤU HÌNH MÀU SẮC (ZEBRA STRIPES) ---
        # Màu trắng cho dòng lẻ
        self.tag_configure('odd', background='#ffffff')
        # Màu xám xanh rất nhạt cho dòng chẵn (hợp với theme hiện đại)
        self.tag_configure('even', background='#f0f4f8') 
        # ----------------------------------------

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
            
            # --- CẬP NHẬT MÀU SAU KHI SẮP XẾP ---
            # Tính toán lại dòng chẵn/lẻ để tô màu lại cho đúng thứ tự mới
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.item(k, tags=(tag,))
            # ------------------------------------

        self._sort_desc[col] = not desc

    # --- TỰ ĐỘNG TÔ MÀU KHI THÊM DỮ LIỆU ---
    def insert(self, parent, index, iid=None, **kw):
        # Đếm số dòng hiện có để quyết định màu cho dòng mới
        current_rows = self.get_children(parent)
        row_idx = len(current_rows)
        
        tag = 'even' if row_idx % 2 == 0 else 'odd'
        
        # Thêm tag màu vào danh sách tag của dòng đó
        if 'tags' in kw:
            kw['tags'] = kw['tags'] + (tag,)
        else:
            kw['tags'] = (tag,)
            
        return super().insert(parent, index, iid, **kw)
    # ---------------------------------------

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

    def update_state(self, can_prev: bool, can_next: bool):
        self.btn_prev.configure(state="normal" if can_prev else "disabled")
        self.btn_next.configure(state="normal" if can_next else "disabled")

    def set_page(self, page_idx: int):
        self.lbl.config(text=f"Page {page_idx + 1}")