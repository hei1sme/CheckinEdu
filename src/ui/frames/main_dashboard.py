import customtkinter as ctk

class MainDashboard(ctk.CTkFrame):
    def __init__(self, parent, view_model):
        super().__init__(parent, fg_color="#F9F9F9")
        self.view_model = view_model
        self.parent = parent # Store a reference to the main App window

        # --- WIDGETS ---
        self.label = ctk.CTkLabel(
            self,
            text="Main Dashboard",
            font=ctk.CTkFont(family="Poppins", size=24, weight="bold"),
            text_color="#333333"
        )
        self.label.pack(pady=20, padx=60)

        self.admin_button = ctk.CTkButton(
            self,
            text="Go to Admin Panel",
            # --- UPDATE THE COMMAND ---
            command=self.parent.request_admin_login_dialog,
            font=ctk.CTkFont(family="Poppins", size=14),
            fg_color="#ED6B1D",
            hover_color="#BF5616"
        )
        self.admin_button.pack(pady=10)