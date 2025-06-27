import customtkinter as ctk

class AdminPanel(ctk.CTkFrame):
    def __init__(self, parent, view_model):
        super().__init__(parent, fg_color="#F0F0F0") # Slightly different bg to distinguish
        self.view_model = view_model

        # --- WIDGETS ---
        self.label = ctk.CTkLabel(
            self,
            text="Admin Panel",
            font=ctk.CTkFont(family="Poppins", size=24, weight="bold"),
            text_color="#333333"
        )
        self.label.pack(pady=20, padx=60)
        
        self.setup_label = ctk.CTkLabel(
            self,
            text="This is where you will manage courses and enroll students.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#666666"
        )
        self.setup_label.pack(pady=5)
        
        self.dashboard_button = ctk.CTkButton(
            self,
            text="Back to Dashboard",
            command=self.view_model.go_to_dashboard,
            font=ctk.CTkFont(family="Poppins", size=14),
            fg_color="#3498DB",
            hover_color="#2874A6"
        )
        self.dashboard_button.pack(pady=20)