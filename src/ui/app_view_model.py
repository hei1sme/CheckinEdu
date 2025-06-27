from src.core import data_manager, face_engine, input_validator # Add input_validator
import os
import pickle
import cv2
from dotenv import load_dotenv # For loading .env file

# Load environment variables from .env file
load_dotenv()

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
        # --- UI STATE VARIABLES ---
        # We need to know which course is selected to add a class to it
        # --- REPLACED ctk.StringVar with a simple string ---
        self.selected_course_for_class_add = "" # Just a regular Python string

        # --- NEW ENROLLMENT STATE ---
        self.enrollment_session_queue = [] # List of students to enroll
        self.current_enrollment_student = None # The student currently being captured
        self.capture_step = 0 # 0=not started, 1=straight, 2=left, etc.
        self.capture_prompts = [
            "CAPTURE COMPLETE", # Index 0 is a placeholder for completion
            "Step 1/5: Look STRAIGHT at Camera",
            "Step 2/5: Turn Head SLIGHTLY LEFT",
            "Step 3/5: Turn Head SLIGHTLY RIGHT",
            "Step 4/5: Look SLIGHTLY UP",
            "Step 5/5: Look SLIGHTLY DOWN (Natural)",
        ]

        # --- CALLBACKS for UI updates ---
        self.update_enrollment_queue_callback = None # To update the listbox
        self.update_capture_prompt_callback = None # To update the video overlay text

        # Get passcode from environment variable
        self.admin_passcode = os.getenv("ADMIN_PASSCODE")

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

        # --- FIX: Check the dictionary directly, not a 'courses' key ---
        if not self.courses_data: # This now checks if the dictionary itself is empty
            print("No courses found. Directing to Admin Panel for setup.")
            self.show_frame("AdminPanel")
        else:
            print("Courses found. Starting on Main Dashboard.")
            self.show_frame("MainDashboard")
            
    # --- COMMANDS (will be expanded in later phases) ---
    def request_admin_login(self, password_attempt):
        """Verifies the admin passcode."""
        if password_attempt == self.admin_passcode:
            self.is_admin_logged_in = True
            self.show_frame("AdminPanel")
            return "SUCCESS"
        else:
            return "FAILED"
        
    def go_to_dashboard(self):
        print("Navigating to dashboard...")
        self.is_admin_logged_in = False # "Log out" when leaving admin panel
        self.show_frame("MainDashboard")

    # --- COMMANDS ARE NOW PURE LOGIC, RETURNING DATA/STATUS ---
    def add_course(self, course_name):
        if not course_name:
            return "EMPTY_INPUT" # Return a status code
        
        success = data_manager.add_course(course_name)
        if success:
            # Refresh internal data
            self.courses_data = data_manager.load_data()
            return "SUCCESS"
        else:
            return "ALREADY_EXISTS"
            
    def add_class_to_course(self, course_name, class_name):
        if not course_name or course_name == "No courses available":
            return "NO_COURSE_SELECTED"
        if not class_name:
            return "EMPTY_INPUT"
            
        success = data_manager.add_class_to_course(course_name, class_name)
        if success:
            # Refresh internal data
            self.courses_data = data_manager.load_data()
            return "SUCCESS"
        else:
            return "ALREADY_EXISTS"

    def get_course_names(self):
        return data_manager.get_courses()

    # --- NEW COMMANDS for Enrollment ---
    def add_student_to_session(self, student_id, student_name, student_class): # Add class as a parameter
        # 1. Validate input
        if not input_validator.is_valid_student_id(student_id):
            return "INVALID_ID"
        
        # --- NEW: FORMAT THE NAME ---
        formatted_name = student_name.replace(" ", "")
        if not input_validator.is_valid_full_name(student_name): # Validate original name
            return "INVALID_NAME"
        
        if not student_class or student_class == "No classes available":
            return "NO_CLASS_SELECTED"
            
        # 2. Check for duplicates
        for student in self.enrollment_session_queue:
            if student['id'] == student_id:
                return "DUPLICATE_IN_SESSION"
        
        # 3. Add to queue with formatted name and class
        student_data = {'id': student_id, 'name': formatted_name, 'class': student_class}
        self.enrollment_session_queue.append(student_data)
        self.update_ui_enrollment_queue()
        return "SUCCESS"

    def get_classes_for_course(self, course_name):
        return data_manager.get_classes_for_course(course_name)

    def start_capture_for_student(self, student_id):
        """Initiates the capture process for a selected student."""
        for student in self.enrollment_session_queue:
            if student['id'] == student_id:
                self.current_enrollment_student = student
                self.capture_step = 1 # Start with step 1
                self.update_ui_capture_prompt()
                return
    
    def capture_image_for_enrollment(self, frame):
        """Saves a frame for the currently selected student."""
        if not self.current_enrollment_student or self.capture_step == 0:
            return # Not in capture mode
        
        # Create folder for student if it doesn't exist
        # --- UPDATE FOLDER NAME FORMAT ---
        student_folder_name = f"{self.current_enrollment_student['id']}_{self.current_enrollment_student['name']}_{self.current_enrollment_student['class']}"
        student_dir = os.path.join(face_engine.KNOWN_FACES_DIR, student_folder_name)
        os.makedirs(student_dir, exist_ok=True)
        
        # Save the image
        file_path = os.path.join(student_dir, f"{self.capture_step}.jpg")
        cv2.imwrite(file_path, frame) # We need to import cv2
        print(f"Saved image to {file_path}")

        # Move to the next step
        if self.capture_step < 5:
            self.capture_step += 1
        else:
            self.capture_step = 0 # Mark as complete
            self.current_enrollment_student = None

        self.update_ui_capture_prompt()

    # --- NEW DELETION COMMANDS ---
    def remove_course(self, course_name):
        if not course_name or course_name in ["Loading...", "No courses yet"]:
            return "NO_COURSE_SELECTED"
        
        success = data_manager.remove_course(course_name)
        if success:
            self.courses_data = data_manager.load_data()
            return "SUCCESS"
        return "FAILED"

    def remove_class(self, course_name, class_name):
        if not course_name or course_name in ["Loading...", "No courses yet"]:
            return "NO_COURSE_SELECTED"
        if not class_name or class_name in ["Select a course first", "No classes yet"]:
            return "NO_CLASS_SELECTED"
            
        success = data_manager.remove_class_from_course(course_name, class_name)
        if success:
            self.courses_data = data_manager.load_data()
            return "SUCCESS"
        return "FAILED"

    # --- NEW COMMAND for Training ---
    def retrain_model(self):
        """
        Calls the face_engine to re-encode all faces in the known_faces directory.
        Returns the number of faces/images encoded.
        """
        # This is a synchronous call, so the UI will freeze briefly.
        # For this project, showing a "Training..." message is sufficient.
        num_encoded = face_engine.encode_known_faces()
        
        # After training, we need to reload the known face data into the ViewModel
        if os.path.exists(face_engine.MODEL_PATH):
            with open(face_engine.MODEL_PATH, 'rb') as f:
                self.known_face_data = pickle.load(f)
        
        return num_encoded

    # --- UI UPDATE METHODS ---
    def set_callbacks(self, show_frame, update_queue, update_prompt):
        """Sets multiple callbacks from the UI at once."""
        self._show_frame_callback = show_frame
        self.update_enrollment_queue_callback = update_queue
        self.update_capture_prompt_callback = update_prompt

    def update_ui_enrollment_queue(self):
        """Calls the UI callback to refresh the queue listbox."""
        if self.update_enrollment_queue_callback:
            self.update_enrollment_queue_callback(self.enrollment_session_queue)

    def update_ui_capture_prompt(self):
        """Calls the UI callback to update the video overlay prompt."""
        if self.update_capture_prompt_callback:
            prompt = self.capture_prompts[self.capture_step]
            self.update_capture_prompt_callback(prompt)