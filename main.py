import customtkinter as ctk
from tkinter import simpledialog, messagebox
from src.ui.app_view_model import AppViewModel
from src.ui.frames.main_dashboard import MainDashboard
from src.ui.frames.admin_panel import AdminPanel
import os

class App(ctk.CTk):
    def __init__(self, app_view_model: AppViewModel):
        super().__init__()
        self.app_vm = app_view_model
        self.current_frame_name = None # Keep track of the visible frame

        # --- CONFIGURE WINDOW ---
        self.title("CheckinEdu - AI Attendance System")
        self.geometry("1920x1080")
        self.state('zoomed')  # Launch in maximized window
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
            frame.grid(row=0, column=0, sticky="nsew")
        
        # --- BIND VIEW MODEL TO VIEW ---
        admin_panel_instance = self.frames["AdminPanel"]
        self.app_vm.set_callbacks(
            show_frame=self.show_frame,
            update_queue=admin_panel_instance.update_session_listbox,
            update_prompt=admin_panel_instance.update_capture_prompt
        )
        
        # --- BIND KEY PRESS TO THE TOP-LEVEL WINDOW ---
        self.bind("<space>", self.on_spacebar_press)

        # --- STARTUP ---
        self.app_vm.initialize_app()

    def show_frame(self, page_name):
        """Raises the specified frame to the top and handles camera/data state."""
        self.current_frame_name = page_name
        frame = self.frames[page_name]
        
        if page_name == "AdminPanel":
            self.frames["AdminPanel"].video_capture.start_capture()
        else: # This includes the MainDashboard
            self.frames["AdminPanel"].video_capture.stop_capture()
            
        # --- THE FIX IS HERE ---
        # If we are showing the dashboard, tell it to refresh its data
        if page_name == "MainDashboard":
            self.frames["MainDashboard"].on_show()
            
        frame.tkraise()
    
    def on_spacebar_press(self, event):
        """
        This app-level event handler delegates the spacebar press to the
        AdminPanel if it's the currently active frame.
        """
        # Only trigger the capture if the Admin Panel is visible
        if self.current_frame_name == "AdminPanel":
            admin_panel = self.frames["AdminPanel"]
            # Call the specific handler method on the admin_panel instance
            admin_panel.handle_spacebar_capture()

    def request_admin_login_dialog(self):
        """Opens a dialog to ask for the admin password."""
        password = simpledialog.askstring("Admin Login", "Enter Admin Passcode:", show='*')
        if password: # If user didn't click cancel
            status = self.app_vm.request_admin_login(password)
            if status == "FAILED":
                messagebox.showerror("Login Failed", "Incorrect Passcode.")

if __name__ == "__main__":
    app_vm = AppViewModel()
    app = App(app_view_model=app_vm)
    app.mainloop()