import customtkinter as ctk
from src.ui.widgets.video_capture import VideoCapture
from PIL import Image # Import Image from PIL

class MainDashboard(ctk.CTkFrame):
    def __init__(self, parent, view_model):
        super().__init__(parent, fg_color="#F9F9F9")
        self.view_model = view_model
        self.parent = parent

        # --- CONFIGURE GRID ---
        self.grid_columnconfigure(0, weight=1, uniform="a")
        self.grid_columnconfigure(1, weight=2, uniform="a")
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT FRAME: CONTROLS ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # --- Right FRAME: Live View ---
        self.live_view_frame = ctk.CTkFrame(self, fg_color="black") # Black background for camera
        self.live_view_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        
        # --- WIDGETS FOR CONTROLS FRAME ---
        # 0. School Logo and Text
        self.logo_image = ctk.CTkImage(Image.open("assets/school_logo.png"), size=(534, 150)) # Resized to maintain aspect ratio
        self.logo_label = ctk.CTkLabel(self.controls_frame, image=self.logo_image, text="")
        self.logo_label.pack(pady=(0, 10), anchor="center")

        

        # 1. Title
        self.title_label = ctk.CTkLabel(self.controls_frame, text="CheckinEdu", font=ctk.CTkFont(family="Playfair Display", size=32, weight="bold"), text_color="#ED6B1D")
        self.title_label.pack(pady=(0, 20), anchor="w")

        # 2. Course and Class Selection
        self.course_label = ctk.CTkLabel(self.controls_frame, text="Select Course", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.course_label.pack(anchor="w")
        self.course_dropdown = ctk.CTkOptionMenu(self.controls_frame, values=["Loading..."])
        self.course_dropdown.pack(fill="x", pady=(0, 10))

        self.class_label = ctk.CTkLabel(self.controls_frame, text="Select Class", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.class_label.pack(anchor="w")
        self.class_dropdown = ctk.CTkOptionMenu(self.controls_frame, values=["Select a course first"])
        self.class_dropdown.pack(fill="x", pady=(0, 20))
        
        # 3. Recognition Sensitivity
        self.tolerance_label = ctk.CTkLabel(self.controls_frame, text="Recognition Sensitivity:", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.tolerance_label.pack(anchor="w")
        self.tolerance_value_label = ctk.CTkLabel(self.controls_frame, text="", font=ctk.CTkFont(family="Inter", size=12), text_color="#333333")
        self.tolerance_value_label.pack(anchor="w", padx=5)
        self.tolerance_slider = ctk.CTkSlider(self.controls_frame, from_=0.4, to=0.7, number_of_steps=6)
        self.tolerance_slider.set(0.5)
        self.tolerance_slider.pack(fill="x", pady=(0, 20))

        # 4. Action Buttons
        self.start_button = ctk.CTkButton(self.controls_frame, text="Start Attendance", fg_color="#ED6B1D", hover_color="#BF5616", font=ctk.CTkFont(family="Poppins", size=14, weight="bold"))
        self.start_button.pack(fill="x", pady=5)
        self.admin_button = ctk.CTkButton(self.controls_frame, text="Admin Panel", command=self.parent.request_admin_login_dialog, font=ctk.CTkFont(family="Poppins", size=14, weight="bold"))
        self.admin_button.pack(fill="x", pady=5)
        self.exit_button = ctk.CTkButton(self.controls_frame, text="Finish & Exit", fg_color="#666666", hover_color="#555555", font=ctk.CTkFont(family="Poppins", size=14, weight="bold"))
        self.exit_button.pack(fill="x", side="bottom") # Puts it at the bottom
        
        # 5. Status Log
        self.status_label = ctk.CTkLabel(self.controls_frame, text="Status Log", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.status_label.pack(anchor="w", pady=(20, 0))
        self.status_log = ctk.CTkTextbox(self.controls_frame, height=150, font=ctk.CTkFont(family="Inter", size=12))
        self.status_log.pack(expand=True, fill="both", anchor="s")
        self.status_log.configure(state="disabled")

        # --- WIDGETS FOR LIVE VIEW FRAME ---
        self.video_capture = VideoCapture(self.live_view_frame, "Press 'Start Attendance' to begin", self.view_model)
        self.video_capture.pack(expand=True, fill="both")

        # --- Store a reference to the ViewModel's app_window_ref ---
        # This is needed for the 'after' loop in the ViewModel
        self.view_model.app_window_ref = parent

        # --- BIND VIEWMODEL CALLBACKS ---
        self.view_model.set_dashboard_callbacks(
            update_status=self.log_to_status_box,
            update_faces=self.video_capture.set_recognized_faces
        )

        # --- CONNECT WIDGETS ---
        self.course_dropdown.configure(command=self.on_course_selected)
        self.start_button.configure(command=self.toggle_attendance)
        self.exit_button.configure(command=self.parent.destroy) # Closes the app
        self.tolerance_slider.configure(command=self.update_tolerance_label)
        self.update_tolerance_label(self.tolerance_slider.get()) # Set initial value

    # --- RENAME refresh_dropdowns to on_show ---
    def on_show(self):
        """This method is called by the main App when this frame is shown."""
        courses = self.view_model.get_course_names() or ["No courses available"]
        current_course = self.course_dropdown.get()
        
        self.course_dropdown.configure(values=courses)
        # If the previously selected course still exists, keep it. Otherwise, default to the first.
        if current_course in courses:
            self.course_dropdown.set(current_course)
        else:
            self.course_dropdown.set(courses[0])
        
        self.on_course_selected(self.course_dropdown.get())

    def on_course_selected(self, course):
        classes = self.view_model.get_classes_for_course(course) or ["No classes available"]
        current_class = self.class_dropdown.get()
        
        self.class_dropdown.configure(values=classes)
        if current_class in classes:
            self.class_dropdown.set(current_class)
        else:
            self.class_dropdown.set(classes[0])

    def log_to_status_box(self, message, level):
        # Simple fix to prevent UI freezing from too many logs
        current_logs = self.status_log.get("1.0", "end-1c").split('\n')
        if len(current_logs) > 50:
            self.status_log.delete("50.0", "end")
        self.status_log.configure(state="normal")
        # You can add color-coding here later based on the 'level'
        self.status_log.insert("0.0", f"{message}\n")
        self.status_log.configure(state="disabled")

    def toggle_attendance(self):
        if self.view_model.is_attendance_running:
            # --- STOP ---
            self.view_model.stop_attendance_loop()
            self.video_capture.stop_capture()
        else:
            # --- START ---
            course = self.course_dropdown.get()
            s_class = self.class_dropdown.get()
            tolerance = self.tolerance_slider.get()
            self.video_capture.start_capture()
            self.view_model.start_attendance_loop(self.video_capture.get_frame, course, s_class, tolerance)
        
        # Update button state based on the view model's current state
        if self.view_model.is_attendance_running:
            self.start_button.configure(text="Stop Attendance", fg_color="red", hover_color="#A00000")
        else:
            self.start_button.configure(text="Start Attendance", fg_color="#ED6B1D", hover_color="#BF5616")

    def update_tolerance_label(self, value):
        self.tolerance_value_label.configure(text=f"Current Value: {value:.2f} (Stricter <-> Looser)")