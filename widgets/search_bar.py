import customtkinter as ctk
from typing import Optional, Callable, List, Dict, Tuple


class SearchBar(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        on_search: Callable[[], None],
        filters: Optional[List[Tuple[str, str, List[str]]]] = None,
        placeholder: str = "Rechercher..."
    ) -> None:
        super().__init__(parent, fg_color='transparent')
        self.on_search = on_search
        self.filter_vars: Dict[str, ctk.StringVar] = {}

        ctk.CTkLabel(self, text="Recherche:", text_color='#333333').pack(side='left')
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, width=150, placeholder_text=placeholder,
                                          textvariable=self.search_var)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: on_search())

        if filters:
            for label, var_name, values in filters:
                ctk.CTkLabel(self, text=f"{label}:", text_color='#333333').pack(side='left', padx=(15, 0))
                self.filter_vars[var_name] = ctk.StringVar(value='Tous')
                combo = ctk.CTkComboBox(
                    self,
                    values=['Tous'] + values,
                    variable=self.filter_vars[var_name],
                    width=130,
                    command=lambda v: on_search()
                )
                combo.pack(side='left', padx=5)

        ctk.CTkButton(self, text="Actualiser", command=on_search,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='right')

    def get_search(self) -> str:
        return self.search_var.get().strip()

    def get_filter(self, var_name: str) -> Optional[str]:
        var = self.filter_vars.get(var_name)
        if var:
            val = var.get()
            return val if val != 'Tous' else None
        return None

    def reset(self) -> None:
        self.search_var.set('')
        for var in self.filter_vars.values():
            var.set('Tous')
        self.on_search()
