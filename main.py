import customtkinter as ctk
from src.ui.app_view_model import AppViewModel
from src.ui.frames.main_dashboard import MainDashboard
from src.ui.frames.admin_panel import AdminPanel

class App(ctk.CTk):
    def __init__(self, app_view_model: AppViewModel):
        super().__init__()
        self.app_vm = app_view_model

        # --- CONFIGURE WINDOW ---
        self.title("CheckinEdu - AI Attendance System")
        self.geometry("1100x580")
        self.configure(fg_color="#F9F9F9")

        # --- CONFIGURE GRID LAYOUT ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- CREATE AND STORE FRAMES ---
        self.frames = {}
        for F in (MainDashboard, AdminPanel):
            page_name = F.__name__
            frame = F(parent=self, view_model=self.app_vm)
            self.frames[page_name] = frame
            # Put all frames in the same spot, the one on top is visible
            frame.grid(row=0, column=0, sticky="nsew")
        
        # --- BIND VIEW MODEL TO VIEW ---
        # This allows the ViewModel to tell the View which frame to show
        self.app_vm.set_show_frame_callback(self.show_frame)

        # --- STARTUP ---
        # Let the ViewModel decide which frame to show first
        self.app_vm.initialize_app()

    def show_frame(self, page_name):
        """Raises the specified frame to the top."""
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app_vm = AppViewModel()
    app = App(app_view_model=app_vm)
    app.mainloop()