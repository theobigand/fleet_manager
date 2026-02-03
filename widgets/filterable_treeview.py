import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Tuple


class FilterableTreeview(tk.Frame):

    def __init__(
        self,
        parent: tk.Widget,
        columns: List[Tuple[str, str, int]],
        on_double_click: Optional[Callable] = None,
        on_right_click: Optional[Callable] = None,
        show_scrollbar: bool = True,
        height: int = 15
    ) -> None:
        super().__init__(parent)
        self.on_double_click = on_double_click
        self.on_right_click = on_right_click
        self.color_tags: Dict[str, str] = {}

        col_ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(self, columns=col_ids, show='headings', height=height)

        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width)

        if show_scrollbar:
            v_scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
            h_scroll = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
            self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

            self.tree.grid(row=0, column=0, sticky='nsew')
            v_scroll.grid(row=0, column=1, sticky='ns')
            h_scroll.grid(row=1, column=0, sticky='ew')

            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
        else:
            self.tree.pack(fill='both', expand=True)

        if on_double_click:
            self.tree.bind('<Double-1>', lambda e: on_double_click())
        if on_right_click:
            self.tree.bind('<Button-3>', self._handle_right_click)

    def _handle_right_click(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            if self.on_right_click:
                self.on_right_click(event)

    def configure_tag(self, tag_name: str, **kwargs) -> None:
        self.tree.tag_configure(tag_name, **kwargs)
        self.color_tags[tag_name] = kwargs.get('background', '')

    def clear(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert(self, values: tuple, tags: tuple = ()) -> str:
        return self.tree.insert('', 'end', values=values, tags=tags)

    def get_selected_tags(self) -> Optional[tuple]:
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0])['tags']

    def get_selected_values(self) -> Optional[tuple]:
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0])['values']

    def get_selected_id(self, tag_index: int = 1) -> Optional[int]:
        tags = self.get_selected_tags()
        if tags and len(tags) > tag_index:
            try:
                return int(tags[tag_index])
            except (ValueError, TypeError):
                pass
        return None
