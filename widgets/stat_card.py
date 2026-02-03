import customtkinter as ctk


class StatCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        title: str,
        value: str,
        color: str
    ) -> None:
        super().__init__(parent, fg_color=color, corner_radius=10)
        self.color = color

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=12),
                     text_color='white').pack(pady=(10, 5))

        self.value_label = ctk.CTkLabel(self, text=value,
                                         font=ctk.CTkFont(size=28, weight='bold'),
                                         text_color='white')
        self.value_label.pack(pady=(5, 10))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)
