import customtkinter as ctk
from src.ui.widgets.video_capture import VideoCapture
from tkinter import messagebox

class AdminPanel(ctk.CTkFrame):
    def __init__(self, parent, view_model):
        super().__init__(parent, fg_color="#F0F0F0", corner_radius=24)
        self.view_model = view_model
        
        # --- 1. CREATE ALL TKINTER VARIABLES ---
        self.mgmt_course_var = ctk.StringVar()
        self.mgmt_class_var = ctk.StringVar()
        self.enroll_course_var = ctk.StringVar()
        self.enroll_class_var = ctk.StringVar()
        
        # --- BENTO GRID: 2 rows, 2 columns, center controls vertically ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="a")
        self.grid_columnconfigure(1, weight=2, uniform="a")

        # --- Modern bento card for controls ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18)
        self.live_view_frame = ctk.CTkFrame(self, fg_color="#181818", corner_radius=24)

        # Center controls_frame vertically and horizontally
        self.controls_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=40, pady=40)
        self.live_view_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 40), pady=40)

        # --- 4. CREATE ALL WIDGETS ---
        self.course_mgmt_label = ctk.CTkLabel(self.controls_frame, text="Course & Class Management", font=ctk.CTkFont(family="Poppins", size=18, weight="bold"), text_color="#333333")
        self.course_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Enter New Course", font=ctk.CTkFont(family="Inter", size=14), corner_radius=8)
        self.add_course_button = ctk.CTkButton(self.controls_frame, text="Add Course", command=self.on_add_course_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        self.mgmt_course_dropdown = ctk.CTkOptionMenu(self.controls_frame, variable=self.mgmt_course_var, values=["Loading..."], command=self.on_mgmt_course_selected, font=ctk.CTkFont(family="Inter", size=14), corner_radius=10)
        self.remove_course_button = ctk.CTkButton(self.controls_frame, text="Delete Selected Course", fg_color="red", hover_color="#C0392B", command=self.on_remove_course_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        self.class_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Enter New Class for Selected Course", font=ctk.CTkFont(family="Inter", size=14), corner_radius=8)
        self.add_class_button = ctk.CTkButton(self.controls_frame, text="Add Class", command=self.on_add_class_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        self.mgmt_class_dropdown = ctk.CTkOptionMenu(self.controls_frame, variable=self.mgmt_class_var, values=["Select course"], font=ctk.CTkFont(family="Inter", size=14), corner_radius=10)
        self.remove_class_button = ctk.CTkButton(self.controls_frame, text="Delete Selected Class", fg_color="red", hover_color="#C0392B", command=self.on_remove_class_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        
        self.enroll_mgmt_label = ctk.CTkLabel(self.controls_frame, text="Student Enrollment", font=ctk.CTkFont(family="Poppins", size=18, weight="bold"), text_color="#333333")
        self.student_id_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Student ID (e.g., SE194127)", font=ctk.CTkFont(family="Inter", size=14), corner_radius=8)
        self.student_name_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Full Name (e.g., Le Nguyen Gia Hung)", font=ctk.CTkFont(family="Inter", size=14), corner_radius=8)
        self.enroll_course_dropdown = ctk.CTkOptionMenu(self.controls_frame, variable=self.enroll_course_var, values=["Loading..."], command=self.on_enroll_course_selected, font=ctk.CTkFont(family="Inter", size=14), corner_radius=10)
        self.enroll_class_dropdown = ctk.CTkOptionMenu(self.controls_frame, variable=self.enroll_class_var, values=["Select a course first"], font=ctk.CTkFont(family="Inter", size=14), corner_radius=10)
        self.add_student_button = ctk.CTkButton(self.controls_frame, text="Add Student to Session", command=self.on_add_student_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        self.session_list_frame = ctk.CTkScrollableFrame(self.controls_frame, height=100, label_text="Session Queue", corner_radius=10)
        
        self.retrain_button = ctk.CTkButton(
            self.controls_frame, 
            text="Re-Train Model", 
            fg_color="#3498DB", 
            hover_color="#2874A6",
            command=self.on_retrain_click, # Add the command
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            corner_radius=10
        )

        self.settings_label = ctk.CTkLabel(self.controls_frame, text="Application Settings", font=ctk.CTkFont(family="Poppins", size=18, weight="bold"), text_color="#333333")
        self.threshold_label = ctk.CTkLabel(self.controls_frame, text="Confirmation Threshold (frames):", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.threshold_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="e.g., 3", font=ctk.CTkFont(family="Inter", size=14), corner_radius=8)
        self.camera_index_label = ctk.CTkLabel(self.controls_frame, text="Camera Index:", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.camera_index_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="e.g., 0", font=ctk.CTkFont(family="Inter", size=14), corner_radius=8)
        self.save_settings_button = ctk.CTkButton(self.controls_frame, text="Save Settings", command=self.on_save_settings_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        self.dashboard_button = ctk.CTkButton(self.controls_frame, text="Back to Dashboard", fg_color="#666666", hover_color="#555555", command=self.on_back_to_dashboard_click, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"), corner_radius=10)
        
        self.video_capture = VideoCapture(self.live_view_frame, "Admin Panel Live View", self.view_model)
        self.video_capture.pack(expand=True, fill="both", padx=24, pady=24)
        # Set the flash effect callback for enrollment feedback
        self.view_model.set_flash_effect_callback(self.video_capture.flash_effect)

        # Set the camera overlay callback for enrollment feedback
        def overlay_callback(text, duration_ms=None):
            if duration_ms is not None:
                self.video_capture.set_overlay_text(text, duration_ms=duration_ms)
            else:
                self.video_capture.set_overlay_text(text)
        self.view_model.set_camera_overlay_callback(overlay_callback)
        # Set the camera progress callback for image count feedback
        self.view_model.set_camera_progress_callback(self.video_capture.set_progress_overlay_text)
        # --- 5. PLACE ALL WIDGETS ON THE GRID ---
        row = 0
        self.course_mgmt_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10)); row+=1
        self.course_entry.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 5)); row+=1
        self.add_course_button.grid(row=row, column=0, columnspan=2, sticky="ew"); row+=1
        self.mgmt_course_dropdown.grid(row=row, column=0, sticky="ew", padx=(0,5));
        self.remove_course_button.grid(row=row, column=1, sticky="ew", padx=(5,0)); row+=1
        self.class_entry.grid(row=row, column=0, sticky="ew", padx=(0,5), pady=(5,0));
        self.add_class_button.grid(row=row, column=1, sticky="ew", padx=(5,0), pady=(5,0)); row+=1
        self.mgmt_class_dropdown.grid(row=row, column=0, sticky="ew", padx=(0,5));
        self.remove_class_button.grid(row=row, column=1, sticky="ew", padx=(5,0)); row+=1
        
        self.enroll_mgmt_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 10)); row+=1
        self.student_id_entry.grid(row=row, column=0, columnspan=2, sticky="ew"); row+=1
        self.student_name_entry.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5); row+=1
        self.enroll_course_dropdown.grid(row=row, column=0, columnspan=2, sticky="ew"); row+=1
        self.enroll_class_dropdown.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5); row+=1
        self.add_student_button.grid(row=row, column=0, columnspan=2, sticky="ew"); row+=1
        self.session_list_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=5); row+=1
        
        self.retrain_button.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(20, 5)); row+=1

        self.settings_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 10)); row+=1
        self.threshold_label.grid(row=row, column=0, sticky="w");
        self.threshold_entry.grid(row=row, column=1, sticky="ew", padx=(5,0)); row+=1
        self.camera_index_label.grid(row=row, column=0, sticky="w");
        self.camera_index_entry.grid(row=row, column=1, sticky="ew", padx=(5,0)); row+=1
        self.save_settings_button.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5, 20)); row+=1
        self.dashboard_button.grid(row=row, column=0, columnspan=2, sticky="ew"); row+=1

        # --- 6. BIND CALLBACKS & INITIALIZE ---
        self.view_model.update_enrollment_queue_callback = self.update_session_listbox
        self.view_model.update_capture_prompt_callback = self.update_capture_prompt
        self.refresh_all_dropdowns()

    # --- UI EVENT HANDLERS ---
    def on_add_course_click(self):
        course_name = self.course_entry.get()
        status = self.view_model.add_course(course_name)
        if status == "SUCCESS":
            messagebox.showinfo("Success", f"Course '{course_name}' added.")
            self.course_entry.delete(0, 'end')
            self.refresh_all_dropdowns()
        else: messagebox.showerror("Error", "Could not add course. It may be empty or already exist.")

    def on_add_class_click(self):
        class_name = self.class_entry.get()
        selected_course = self.mgmt_course_var.get()
        status = self.view_model.add_class_to_course(selected_course, class_name)
        if status == "SUCCESS":
            messagebox.showinfo("Success", f"Class '{class_name}' added to {selected_course}.")
            self.class_entry.delete(0, 'end')
            self.refresh_all_dropdowns()
        else: messagebox.showerror("Error", "Could not add class. Check inputs.")
    
    def on_remove_course_click(self):
        course_to_delete = self.mgmt_course_var.get()
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the course '{course_to_delete}' and all its classes?\n\nThis action cannot be undone.", icon='warning'):
            status = self.view_model.remove_course(course_to_delete)
            if status == "SUCCESS":
                messagebox.showinfo("Success", f"Course '{course_to_delete}' has been deleted.")
                self.refresh_all_dropdowns()
            elif status == "NO_COURSE_SELECTED": messagebox.showerror("Error", "No course selected to delete.")
            else: messagebox.showerror("Error", "Could not delete the selected course.")

    def on_remove_class_click(self):
        course = self.mgmt_course_var.get()
        class_to_delete = self.mgmt_class_var.get()
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete class '{class_to_delete}' from course '{course}'?", icon='warning'):
            status = self.view_model.remove_class(course, class_to_delete)
            if status == "SUCCESS":
                messagebox.showinfo("Success", "Class has been deleted.")
                self.refresh_all_dropdowns()
            elif status == "NO_CLASS_SELECTED": messagebox.showerror("Error", "No class selected to delete.")
            else: messagebox.showerror("Error", "Could not delete class.")

    def on_add_student_click(self):
        sid = self.student_id_entry.get()
        name = self.student_name_entry.get()
        s_class = self.enroll_class_var.get()
        status = self.view_model.add_student_to_session(sid, name, s_class)
        if status == "SUCCESS":
            messagebox.showinfo("Success", f"Added '{name}' to the session.")
            self.student_id_entry.delete(0, 'end')
            self.student_name_entry.delete(0, 'end')
        elif status == "INVALID_ID": messagebox.showerror("Error", f"Invalid Student ID format for '{sid}'.\nExpected: SE<yy><nnnn>")
        elif status == "INVALID_NAME": messagebox.showerror("Error", f"Invalid Full Name format for '{name}'.\nExpected: Firstname Lastname (Capitalized)")
        elif status == "NO_CLASS_SELECTED": messagebox.showerror("Error", "Please select a class for the student.")
        elif status == "DUPLICATE_IN_SESSION": messagebox.showwarning("Warning", f"Student with ID '{sid}' is already in this session.")

    def on_mgmt_course_selected(self, selected_course):
        class_list = self.view_model.get_classes_for_course(selected_course)
        if not class_list: class_list = ["No classes exist"]
        self.mgmt_class_dropdown.configure(values=class_list)
        self.mgmt_class_dropdown.set(class_list[0])

    def on_enroll_course_selected(self, selected_course):
        class_list = self.view_model.get_classes_for_course(selected_course)
        if not class_list: class_list = ["No classes yet"]
        self.enroll_class_dropdown.configure(values=class_list)
        self.enroll_class_dropdown.set(class_list[0])

    def refresh_all_dropdowns(self):
        course_list = self.view_model.get_course_names()
        if not course_list: course_list = ["No courses yet"]
        
        self.mgmt_course_dropdown.configure(values=course_list)
        self.enroll_course_dropdown.configure(values=course_list)
        
        default_course = course_list[0]
        self.mgmt_course_var.set(default_course)
        self.enroll_course_var.set(default_course)
        
        self.on_mgmt_course_selected(default_course)
        self.on_enroll_course_selected(default_course)

        # Populate settings
        current_settings = self.view_model.get_app_settings()
        self.threshold_entry.delete(0, 'end')
        self.threshold_entry.insert(0, str(current_settings.get('confirmation_threshold', 3)))
        self.camera_index_entry.delete(0, 'end')
        self.camera_index_entry.insert(0, str(current_settings.get('camera_index', 0)))

    def on_back_to_dashboard_click(self):
        self.video_capture.stop_capture()
        self.view_model.go_to_dashboard()

    def update_session_listbox(self, session_queue):
        for widget in self.session_list_frame.winfo_children(): widget.destroy()
        for student in session_queue:
            container = ctk.CTkFrame(self.session_list_frame, fg_color="transparent")
            container.pack(fill="x", pady=2)
            container.grid_columnconfigure(0, weight=1); container.grid_columnconfigure(1, weight=0)
            label_text = f"{student['id']} - {student['name']} ({student['class']})"
            label = ctk.CTkLabel(container, text=label_text, anchor="w")
            label.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
            button = ctk.CTkButton(container, text="Start Capture", width=100, fg_color="#2ECC71", hover_color="#27AE60", command=lambda s_id=student['id']: self.on_student_select_for_capture(s_id))
            button.grid(row=0, column=1, sticky="e", padx=5, pady=2)

    def update_capture_prompt(self, prompt_text):
        self.video_capture.set_overlay_text(prompt_text)
        
    def on_student_select_for_capture(self, student_id):
        self.view_model.start_capture_for_student(student_id)

    def start_detection_loop(self):
        # This loop runs continuously in the admin panel
        frame = self.video_capture.get_frame()
        if frame is not None:
            # Use the view_model's face_engine to detect faces
            faces = self.view_model.face_engine.detect_faces(frame)
            # Pass raw face rectangles to the video capture widget
            self.video_capture.set_detected_faces(faces)
        # Reschedule the loop
        self.after(100, self.start_detection_loop) # Run every 100ms

    def handle_spacebar_capture(self):
        current_frame = self.video_capture.get_frame()
        if current_frame is not None:
            if self.view_model.current_enrollment_student is not None:
                # Take 5 pictures in quick succession for this step
                for _ in range(self.view_model.CAPTURE_IMAGES_PER_STEP):
                    frame = self.video_capture.get_frame()
                    if frame is not None:
                        self.view_model.capture_image_for_enrollment(frame)
                        self.video_capture.flash_effect()
            else:
                pass
    
    # --- NEW EVENT HANDLER for Re-Train Button ---
    def on_retrain_click(self):
        # Provide immediate feedback to the user that training has started
        self.retrain_button.configure(text="Training in progress...", state="disabled")
        # Use 'after' to allow the UI to update *before* the heavy work starts
        self.after(100, self.perform_retraining)

    def perform_retraining(self):
        """The actual retraining work, called after the UI has updated."""
        try:
            num_faces = self.view_model.retrain_model()
            messagebox.showinfo("Training Complete", f"Successfully trained on {num_faces} images.")
        except ValueError as ve:
            messagebox.showerror("Training Error", f"Could not train model. No faces found for training.\nDetails: {ve}")
        except Exception as e:
            messagebox.showerror("Training Error", f"An error occurred during training: {e}")
        finally:
            # ALWAYS re-enable the button and reset its text
            self.retrain_button.configure(text="Re-Train Model", state="normal")

    def on_save_settings_click(self):
        new_threshold = self.threshold_entry.get()
        new_camera_index = self.camera_index_entry.get()
        status_threshold = self.view_model.save_confirmation_threshold(new_threshold)
        status_camera = self.view_model.save_camera_index(new_camera_index)

        if status_threshold == "SUCCESS" and status_camera == "SUCCESS":
            messagebox.showinfo("Settings Saved", f"Confirmation threshold has been set to {new_threshold}.\nCamera index has been set to {new_camera_index}.")
        elif status_threshold == "INVALID_INPUT" or status_camera == "INVALID_INPUT":
            messagebox.showerror("Invalid Input", "Please enter valid positive numbers for threshold and camera index.")
        else:
            messagebox.showerror("Error", "An unexpected error occurred while saving settings.")

    def _validate_numeric_input(self, P):
        if P.isdigit() or P == "":
            return True
        else:
            return False