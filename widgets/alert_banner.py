import customtkinter as ctk


class AlertBanner(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        message: str,
        bg_color: str = '#e74c3c',
        fg_color: str = 'white'
    ) -> None:
        super().__init__(parent, fg_color=bg_color, corner_radius=8)

        self.label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=fg_color
        )
        self.label.pack(pady=10)

    def set_message(self, message: str) -> None:
        self.label.configure(text=message)

    def show(self, **pack_options) -> None:
        defaults = {'fill': 'x', 'padx': 20, 'pady': (0, 10)}
        defaults.update(pack_options)
        self.pack(**defaults)

    def hide(self) -> None:
        self.pack_forget()
