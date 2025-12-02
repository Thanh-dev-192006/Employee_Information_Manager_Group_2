import tkinter as tk
from tkinter import ttk

class Dashboard(ttk.Frame):
    def __init__(self, parent, managers: dict):
        super().__init__(parent)
        self.managers = managers

        title = ttk.Label(self, text="Dashboard", font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w", padx=16, pady=(16, 4))

        note = ttk.Label(
            self,
            text="(Khung trống theo yêu cầu đề bài - nhóm có thể bổ sung biểu đồ/overview sau)",
            foreground="#666",
        )
        note.pack(anchor="w", padx=16, pady=(0, 16))