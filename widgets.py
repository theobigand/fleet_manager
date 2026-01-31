import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, List, Dict, Any, Tuple


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


class BaseFormDialog(tk.Toplevel):
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        width: int = 450,
        height: int = 400
    ) -> None:
        super().__init__(parent)
        self.result: Optional[Dict[str, Any]] = None
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(bg='#ffffff')

        self.transient(parent)
        self.grab_set()

        self.form_frame = tk.Frame(self, bg='#ffffff')
        self.form_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        self.vars: Dict[str, tk.Variable] = {}
        self.current_row = 0
    
    def add_section_title(self, text: str) -> None:
        tk.Label(
            self.form_frame,
            text=text,
            font=('Helvetica', 12, 'bold'),
            bg='#ffffff',
            fg='#000000'
        ).grid(row=self.current_row, column=0, columnspan=2, sticky='w', pady=(10, 10))
        self.current_row += 1
    
    def add_entry(
        self,
        label: str,
        var_name: str,
        default: str = "",
        show: Optional[str] = None,
        width: int = 30
    ) -> ttk.Entry:
        tk.Label(self.form_frame, text=label, bg='#ffffff', fg='#000000').grid(
            row=self.current_row, column=0, sticky='e', padx=(0, 10), pady=5
        )

        self.vars[var_name] = tk.StringVar(value=default)
        entry = ttk.Entry(
            self.form_frame,
            textvariable=self.vars[var_name],
            width=width,
            show=show
        )
        entry.grid(row=self.current_row, column=1, sticky='w', pady=5)
        self.current_row += 1
        return entry
    
    def add_combobox(
        self,
        label: str,
        var_name: str,
        values: List[str],
        default: str = "",
        width: int = 27,
        state: str = 'readonly'
    ) -> ttk.Combobox:
        tk.Label(self.form_frame, text=label, bg='#ffffff', fg='#000000').grid(
            row=self.current_row, column=0, sticky='e', padx=(0, 10), pady=5
        )

        self.vars[var_name] = tk.StringVar(value=default)
        combo = ttk.Combobox(
            self.form_frame,
            textvariable=self.vars[var_name],
            values=values,
            state=state,
            width=width
        )
        combo.grid(row=self.current_row, column=1, sticky='w', pady=5)
        self.current_row += 1
        return combo
    
    def add_checkbox(
        self,
        label: str,
        var_name: str,
        default: bool = False
    ) -> ttk.Checkbutton:
        tk.Label(self.form_frame, text=label, bg='#ffffff', fg='#000000').grid(
            row=self.current_row, column=0, sticky='e', padx=(0, 10), pady=5
        )
        
        self.vars[var_name] = tk.BooleanVar(value=default)
        check = ttk.Checkbutton(self.form_frame, variable=self.vars[var_name])
        check.grid(row=self.current_row, column=1, sticky='w', pady=5)
        self.current_row += 1
        return check
    
    def add_text(
        self,
        label: str,
        var_name: str,
        width: int = 30,
        height: int = 3
    ) -> tk.Text:
        tk.Label(self.form_frame, text=label, bg='#ffffff', fg='#000000').grid(
            row=self.current_row, column=0, sticky='ne', padx=(0, 10), pady=5
        )
        
        text_widget = tk.Text(self.form_frame, width=width, height=height,
                             bg='#ffffff', fg='#000000', insertbackground='#000000')
        text_widget.grid(row=self.current_row, column=1, sticky='w', pady=5)
        self.vars[var_name] = text_widget
        self.current_row += 1
        return text_widget
    
    def add_file_picker(
        self,
        label: str,
        var_name: str,
        filetypes: List[Tuple[str, str]] = None
    ) -> ttk.Entry:
        tk.Label(self.form_frame, text=label, bg='#ffffff', fg='#000000').grid(
            row=self.current_row, column=0, sticky='e', padx=(0, 10), pady=5
        )

        file_frame = tk.Frame(self.form_frame, bg='#ffffff')
        file_frame.grid(row=self.current_row, column=1, sticky='w', pady=5)

        self.vars[var_name] = tk.StringVar()
        entry = ttk.Entry(file_frame, textvariable=self.vars[var_name], width=22)
        entry.pack(side='left')

        def browse() -> None:
            ft = filetypes or [("Tous les fichiers", "*.*")]
            filename = filedialog.askopenfilename(filetypes=ft)
            if filename:
                self.vars[var_name].set(filename)

        tk.Button(
            file_frame, text="...", command=browse,
            bg='#cccccc', fg='#000000', relief='flat'
        ).pack(side='left', padx=2)
        
        self.current_row += 1
        return entry
    
    def add_buttons(
        self,
        on_save: Callable,
        save_text: str = "Enregistrer",
        cancel_text: str = "Annuler"
    ) -> None:
        btn_frame = tk.Frame(self.form_frame, bg='#ffffff')
        btn_frame.grid(row=self.current_row, column=0, columnspan=2, pady=25)

        tk.Button(
            btn_frame,
            text=save_text,
            command=on_save,
            bg='#27ae60',
            fg='#000000',
            font=('Helvetica', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=5
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text=cancel_text,
            command=self.destroy,
            bg='#e74c3c',
            fg='#000000',
            relief='flat',
            padx=20,
            pady=5
        ).pack(side='left', padx=5)
    
    def get_value(self, var_name: str) -> Any:
        var = self.vars.get(var_name)
        if var is None:
            return None
        if isinstance(var, tk.Text):
            return var.get('1.0', 'end-1c')
        return var.get()
    
    def set_value(self, var_name: str, value: Any) -> None:
        var = self.vars.get(var_name)
        if var is None:
            return
        if isinstance(var, tk.Text):
            var.delete('1.0', 'end')
            var.insert('1.0', str(value) if value else "")
        elif isinstance(var, tk.BooleanVar):
            var.set(bool(value))
        else:
            var.set(str(value) if value is not None else "")
    
    def show_error(self, message: str) -> None:
        messagebox.showerror("Erreur", message)
    
    def show_success(self, message: str) -> None:
        messagebox.showinfo("Succès", message)


class StatCard(tk.Frame):
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        value: str,
        color: str
    ) -> None:
        super().__init__(parent, bg='white', relief='solid', borderwidth=1)
        
        self.color = color
        
        tk.Frame(self, bg=color, height=5).pack(fill='x')
        
        self.value_label = tk.Label(
            self,
            text=value,
            font=('Helvetica', 28, 'bold'),
            bg='white',
            fg=color
        )
        self.value_label.pack(pady=(15, 5))
        
        tk.Label(
            self,
            text=title,
            font=('Helvetica', 9),
            bg='white',
            fg='#7f8c8d'
        ).pack(pady=(0, 15))
    
    def set_value(self, value: str) -> None:
        self.value_label.config(text=value)


class AlertBanner(tk.Frame):

    def __init__(
        self,
        parent: tk.Widget,
        message: str,
        bg_color: str = '#e74c3c',
        fg_color: str = '#000000'
    ) -> None:
        super().__init__(parent, bg=bg_color)

        self.label = tk.Label(
            self,
            text=message,
            font=('Helvetica', 11, 'bold'),
            bg=bg_color,
            fg=fg_color,
            pady=10
        )
        self.label.pack()
    
    def set_message(self, message: str) -> None:
        self.label.config(text=message)
    
    def show(self) -> None:
        self.pack(fill='x', padx=20, pady=(0, 10))
    
    def hide(self) -> None:
        self.pack_forget()


class SearchBar(tk.Frame):

    def __init__(
        self,
        parent: tk.Widget,
        on_search: Callable[[], None],
        filters: Optional[List[Tuple[str, str, List[str]]]] = None
    ) -> None:
        super().__init__(parent, bg='#ffffff')
        self.on_search = on_search
        self.vars: Dict[str, tk.StringVar] = {}

        tk.Label(self, text="Recherche:", bg='#ffffff', fg='#000000').pack(side='left')
        self.vars['search'] = tk.StringVar()
        self.vars['search'].trace('w', lambda *args: on_search())
        ttk.Entry(self, textvariable=self.vars['search'], width=25).pack(side='left', padx=(5, 15))

        if filters:
            for label, var_name, values in filters:
                tk.Label(self, text=f"{label}:", bg='#ffffff', fg='#000000').pack(side='left')
                self.vars[var_name] = tk.StringVar(value='')
                combo = ttk.Combobox(
                    self,
                    textvariable=self.vars[var_name],
                    values=[''] + values,
                    state='readonly',
                    width=12
                )
                combo.pack(side='left', padx=(5, 15))
                combo.bind('<<ComboboxSelected>>', lambda e: on_search())

        tk.Button(
            self,
            text="Reset",
            command=self.reset,
            bg='#cccccc',
            fg='#000000',
            relief='flat'
        ).pack(side='left')
    
    def get_value(self, var_name: str) -> str:
        return self.vars.get(var_name, tk.StringVar()).get()
    
    def reset(self) -> None:
        for var in self.vars.values():
            var.set('')
        self.on_search()
