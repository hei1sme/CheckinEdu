from src.core import data_manager, face_engine
import os
import pickle

class AppViewModel:
    def __init__(self):
        # --- CALLBACKS ---
        # This will hold the function from the View that shows a frame
        self._show_frame_callback = None

        # --- DATA ---
        self.courses_data = {}
        self.known_face_data = {"encodings": [], "names": []}
        
        # --- APPLICATION STATE ---
        self.is_admin_logged_in = False

    def set_show_frame_callback(self, callback):
        """Sets the callback function to switch frames in the UI."""
        self._show_frame_callback = callback
    
    def show_frame(self, page_name):
        """A wrapper to call the UI's frame switching function."""
        if self._show_frame_callback:
            self._show_frame_callback(page_name)

    def load_initial_data(self):
        """Loads all necessary data from the core modules at startup."""
        print("ViewModel: Loading initial data...")
        self.courses_data = data_manager.load_data()
        
        # Load face encodings if the model file exists
        if os.path.exists(face_engine.MODEL_PATH):
            with open(face_engine.MODEL_PATH, 'rb') as f:
                self.known_face_data = pickle.load(f)
        print("ViewModel: Data loaded.")

    def initialize_app(self):
        """
        Initializes the application. Loads data and decides which
        frame to show first based on whether initial setup is needed.
        """
        self.load_initial_data()

        # Guided first-time setup logic
        # If there are no courses defined, force the user to the admin panel
        if not self.courses_data or not self.courses_data['courses']:
            print("No courses found. Directing to Admin Panel for setup.")
            self.show_frame("AdminPanel")
        else:
            print("Courses found. Starting on Main Dashboard.")
            self.show_frame("MainDashboard")
            
    # --- COMMANDS (will be expanded in later phases) ---
    def request_admin_login(self):
        # For now, just a placeholder.
        # In Phase 3, this will open a password dialog.
        print("Admin login requested...")
        self.is_admin_logged_in = True # Simulate successful login
        self.show_frame("AdminPanel")
        
    def go_to_dashboard(self):
        print("Navigating to dashboard...")
        self.is_admin_logged_in = False # "Log out" when leaving admin panel
        self.show_frame("MainDashboard")