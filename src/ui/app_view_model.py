from src.core import data_manager, face_engine_haar_lbph as face_engine, input_validator, attendance_manager, settings_manager
import os
import pickle
import cv2
import threading
import queue
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppViewModel:
    def __init__(self):
        # --- CALLBACKS ---
        self._show_frame_callback = None
        self.update_enrollment_queue_callback = None
        self.update_capture_prompt_callback = None
        self.update_status_log_callback = None
        self.update_video_faces_callback = None
        self.face_engine = face_engine.HaarLBPHFaceEngine() # Create a single instance
        
        # --- DATA ---
        self.courses_data = {}
        
        
        # --- APPLICATION STATE ---
        self.is_admin_logged_in = False
        self.admin_passcode = os.getenv("ADMIN_PASSCODE") # The missing line
        
        # --- ENROLLMENT STATE ---
        self.enrollment_session_queue = []
        self.current_enrollment_student = None
        self.capture_step = 0
        # --- NEW, MORE DETAILED PROMPTS ---
        self.capture_prompts = [
            "CAPTURE COMPLETE", # Index 0
            "Step 1/8: Look STRAIGHT, Neutral Expression",
            "Step 2/8: Look STRAIGHT, Big Smile",
            "Step 3/8: Turn Head SLIGHTLY LEFT",
            "Step 4/8: Turn Head SLIGHTLY RIGHT",
            "Step 5/8: Look SLIGHTLY UP",
            "Step 6/8: Look SLIGHTLY DOWN",
            "Step 7/8: Tilt Head Left",
            "Step 8/8: Tilt Head Right",
        ]
        
        # --- DASHBOARD STATE ---
        self.is_attendance_running = False
        self.students_logged_today = set()
        self.frame_counter = 0
        self.process_every_n_frames = 5 # Increased to reduce CPU load
        self.last_known_faces_with_status = []

        # --- NEW STATE for Confirmation ---
        self.recognition_buffer = {} # Key: student_id, Value: confirmation_count
        self.settings = settings_manager.load_settings()
        self.CONFIRMATION_THRESHOLD = self.settings.get('confirmation_threshold', 8)
        self.camera_index = self.settings.get('camera_index', 0)

        # --- CONSTANTS for Tolerance Mapping ---
        # LBPH confidence: lower is stricter (e.g., 50-100)
        self.TOLERANCE_MAPPING_RANGES = {'lbph': (50, 100)}

        # --- THREADING FOR RECOGNITION ---
        self.recognition_thread = None
        self.recognition_queue = queue.Queue()
        self.stop_recognition_thread = threading.Event()

    def set_show_frame_callback(self, callback):
        """Sets the callback function to switch frames in the UI."""
        self._show_frame_callback = callback
    
    def show_frame(self, page_name):
        """A wrapper to call the UI's frame switching function."""
        if self._show_frame_callback:
            self._show_frame_callback(page_name)

    def load_initial_data(self):
        """Loads all necessary data from the core modules at startup."""
        self.courses_data = data_manager.load_data()
        self.face_engine.load_model() # Let the engine handle its own loading

    def initialize_app(self):
        """
        Initializes the application. Loads data and decides which
        frame to show first based on whether initial setup is needed.
        """
        self.load_initial_data()

        # --- FIX: Check the dictionary directly, not a 'courses' key ---
        if not self.courses_data: # This now checks if the dictionary itself is empty
            self.show_frame("AdminPanel")
        else:
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

    def get_app_settings(self):
        """Returns the current application settings dictionary."""
        return self.settings

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
        """Saves a pre-processed version of the frame for the current student."""
        if not self.current_enrollment_student or self.capture_step == 0:
            return
            
        student_folder_name = f"{self.current_enrollment_student['id']}_{self.current_enrollment_student['name']}_{self.current_enrollment_student['class']}"
        student_dir = os.path.join(face_engine.KNOWN_FACES_DIR, student_folder_name)
        os.makedirs(student_dir, exist_ok=True)
        
        # --- PRE-PROCESSING STEPS ---
        # 1. Detect faces in the frame
        faces = self.face_engine.detect_faces(frame)
        
        if len(faces) == 0:
            self.update_status_log_callback("No face detected in the frame. Skipping image save.", "warning")
            return # Do not increment capture_step if no face is detected
            
        # Assuming only one face per capture for enrollment
        x, y, w, h = faces[0]
        
        # 2. Crop the face from the frame
        face_img = frame[y:y+h, x:x+w]
        
        # 3. Preprocess the cropped face (grayscale, histogram equalization)
        preprocessed_face = self.face_engine.preprocess_face(face_img)
        
        # Save the pre-processed, cropped image
        file_path = os.path.join(student_dir, f"{self.current_enrollment_student['id']}_{self.capture_step}.jpg")
        cv2.imwrite(file_path, preprocessed_face)

        # Move to the next step
        if self.capture_step < 8:
            self.capture_step += 1
        else:
            self.capture_step = 0
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
        try:
            num_encoded = self.face_engine.train_model()
            # After training, reload the model into our instance
            self.face_engine.load_model()
            return num_encoded
        except Exception as e:
            print(f"Error during training: {e}")
            raise e # Re-raise the exception so the UI can catch it

    def save_confirmation_threshold(self, value):
        """Validates and saves the new confirmation threshold."""
        try:
            new_threshold = int(value)
            if new_threshold <= 0: return "INVALID_INPUT"
            self.CONFIRMATION_THRESHOLD = new_threshold
            self.settings['confirmation_threshold'] = new_threshold
            settings_manager.save_settings(self.settings)
            return "SUCCESS"
        except (ValueError, TypeError):
            return "INVALID_INPUT"

    def save_camera_index(self, value):
        """Validates and saves the new camera index."""
        try:
            new_index = int(value)
            if new_index < 0: return "INVALID_INPUT"
            self.camera_index = new_index
            self.settings['camera_index'] = new_index
            settings_manager.save_settings(self.settings)
            return "SUCCESS"
        except (ValueError, TypeError):
            return "INVALID_INPUT"

    # --- UI UPDATE METHODS ---
    def set_callbacks(self, show_frame, update_queue, update_prompt):
        """Sets multiple callbacks from the UI at once."""
        self._show_frame_callback = show_frame
        self.update_enrollment_queue_callback = update_queue
        self.update_capture_prompt_callback = update_prompt

    def set_dashboard_callbacks(self, update_status, update_faces):
        self.update_status_log_callback = update_status
        self.update_video_faces_callback = update_faces

    def update_ui_enrollment_queue(self):
        """Calls the UI callback to refresh the queue listbox."""
        if self.update_enrollment_queue_callback:
            self.update_enrollment_queue_callback(self.enrollment_session_queue)

    def update_ui_capture_prompt(self):
        """Calls the UI callback to update the video overlay prompt."""
        if self.update_capture_prompt_callback:
            prompt = self.capture_prompts[self.capture_step]
            self.update_capture_prompt_callback(prompt)

    # --- THE MAIN RECOGNITION LOOP ---
    def start_attendance_loop(self, get_frame_func, course, class_name, tolerance):
        if not course or course in ["Loading...", "No courses yet"]:
            self.log_status("Error: Please select a valid course.", "error")
            return
        if not class_name or class_name in ["Select a course first", "No classes yet"]:
            self.log_status("Error: Please select a valid class.", "error")
            return

        self.is_attendance_running = True
        self.current_get_frame_func = get_frame_func
        self.current_course = course
        self.current_class_name = class_name
        self.current_tolerance = tolerance
        
        # Ensure any previous recognition thread is stopped before starting a new one
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.stop_attendance_loop() # This will set the stop event and join the thread

        self.stop_recognition_thread.clear() # Ensure the stop event is clear for the new thread
        self.recognition_thread = threading.Thread(target=self._recognition_worker, args=(get_frame_func, course, class_name, tolerance))
        self.recognition_thread.daemon = True # Allow the main program to exit even if thread is running
        self.recognition_thread.start()

        self.log_status(f"Attendance started for {course} - {class_name}", "info")
        # Start the UI update loop
        self.recognition_loop_simple()

    def stop_attendance_loop(self):
        self.is_attendance_running = False
        self.stop_recognition_thread.set() # Signal the worker thread to stop
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=1.0) # Wait for the thread to finish
            if self.recognition_thread.is_alive():
                # Log a warning if the thread didn't terminate gracefully
                pass
        self.log_status("Attendance stopped.", "info")
        # Clear any remaining faces on UI
        if self.update_video_faces_callback: self.update_video_faces_callback([])

    def _recognition_worker(self, get_frame_func, course, class_name, tolerance):
        while not self.stop_recognition_thread.is_set():
            # --- Map UI tolerance slider to LBPH confidence threshold ---
            ui_slider_min, ui_slider_max = 0.4, 0.7 # The UI slider range
            lbph_min, lbph_max = self.TOLERANCE_MAPPING_RANGES['lbph']
            
            # Linear mapping: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
            slope = (lbph_max - lbph_min) / (ui_slider_max - ui_slider_min)
            lbph_confidence_threshold = lbph_min + slope * (tolerance - ui_slider_min)

            frame = get_frame_func()
            if frame is not None:
                self.frame_counter += 1
                if self.frame_counter % self.process_every_n_frames == 0:
                    # --- FIX: Use the single self.face_engine instance ---
                    faces = self.face_engine.detect_faces(frame)
                    faces_with_status = []
                    recognized_ids_in_frame = set()
                    for (x, y, w, h) in faces:
                        face_img = frame[y:y+h, x:x+w]
                        preprocessed = self.face_engine.preprocess_face(face_img)
                        name, confidence = self.face_engine.recognize_face(preprocessed, confidence_threshold=lbph_confidence_threshold)
                        status = "Unknown"
                        match_percent = None
                        student_id = None
                        if name != "Unknown" and confidence is not None:
                            # Convert distance (lower is better) to a match percentage
                            match_percent = max(0, 100 * (1 - (confidence / lbph_confidence_threshold)))
                            student_id = name.split('_')[0]
                            recognized_ids_in_frame.add(student_id)
                            if student_id in self.students_logged_today:
                                status = "Attended"
                                if student_id in self.recognition_buffer:
                                    del self.recognition_buffer[student_id]
                            else:
                                status = "Known"
                                self.recognition_buffer[student_id] = self.recognition_buffer.get(student_id, 0) + 1
                                if self.recognition_buffer[student_id] >= self.CONFIRMATION_THRESHOLD:
                                    was_logged = attendance_manager.log_attendance(name, course, class_name)
                                    if was_logged:
                                        self.students_logged_today.add(student_id)
                                        # Log status on the main thread via queue
                                        log_message = f"Attended: {name.split('_')[1]} ({student_id})"
                                        self.recognition_queue.put(("log_status", (log_message, "success")))
                                        status = "Attended"
                                        del self.recognition_buffer[student_id]
                                    else:
                                        self.students_logged_today.add(student_id)
                                        # Log status on the main thread via queue
                                        log_message = f"Already Logged: {name.split('_')[1]} ({student_id})"
                                        self.recognition_queue.put(("log_status", (log_message, "info")))
                                        status = "Already Logged"
                                        del self.recognition_buffer[student_id]
                                else:
                                    status = f"Verifying ({self.recognition_buffer[student_id]}/{self.CONFIRMATION_THRESHOLD})"
                        faces_with_status.append((name, (y, x+w, y+h, x), status, course, class_name, match_percent))
                    # Put results into the queue for the main thread to pick up
                    self.recognition_queue.put(("update_faces", faces_with_status))
            # Small sleep to prevent busy-waiting and allow other threads to run
            self.stop_recognition_thread.wait(0.01) # Check stop signal every 10ms

    def recognition_loop_simple(self):
        # This is the UI-facing loop, it checks the queue for updates
        if not self.is_attendance_running:
            if self.update_video_faces_callback: self.update_video_faces_callback([])
            return

        try:
            while True:
                # Try to get results from the queue without blocking
                message_type, data = self.recognition_queue.get_nowait()
                if message_type == "update_faces":
                    self.last_known_faces_with_status = data
                    if self.update_video_faces_callback:
                        self.update_video_faces_callback(self.last_known_faces_with_status)
                elif message_type == "log_status":
                    # data is a tuple: (message, level), so we unpack it into the function call
                    self.log_status(*data)
        except queue.Empty:
            pass # No new data in the queue, just continue

        # Schedule the next check for UI updates
        if hasattr(self, 'app_window_ref'):
            self.app_window_ref.after(30, self.recognition_loop_simple)

    def log_status(self, message, level="normal"):
        """Calls the UI to add a message to the status log."""
        if self.update_status_log_callback:
            self.update_status_log_callback(message, level)