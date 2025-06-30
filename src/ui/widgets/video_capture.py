import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import queue

class VideoCapture(ctk.CTkFrame):
    def __init__(self, parent, initial_text="", view_model=None):
        super().__init__(parent, fg_color="black", corner_radius=18)
        self.label_widget = ctk.CTkLabel(self, text="", image=None, corner_radius=12)
        self.label_widget.pack(expand=True, fill="both")
        
        # --- OVERLAY for instructions ---
        self.overlay_label = ctk.CTkLabel(
            self, text=initial_text,
            font=ctk.CTkFont(family="Poppins", size=20, weight="bold"),
            fg_color="#222831", text_color="white", corner_radius=12, padx=16, pady=8
        )
        self.overlay_label.place(relx=0.5, rely=0.1, anchor="center")
        # Warning overlay at center (initially hidden)
        self.overlay_warning_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Poppins", size=20, weight="bold"),
            fg_color="#C0392B", text_color="white", corner_radius=12, padx=16, pady=8
        )
        self.overlay_warning_label.place(relx=0.5, rely=0.5, anchor="center")
        self.overlay_warning_label.lower()  # Hide initially

        # Progress overlay at bottom center
        self.overlay_progress_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
            fg_color="#222831", text_color="white", corner_radius=12, padx=12, pady=6
        )
        self.overlay_progress_label.place(relx=0.5, rely=0.92, anchor="center")
        
        self.cap = None
        self.view_model = view_model
        self.last_frame = None
        self.faces_with_status = [] # Initialize faces_with_status
        self._after_id = None # To store the ID of the scheduled after call

        # --- PERFORMANCE FLAG ---
        self.enable_overlays = True

        # --- THREADING FOR IMAGE PROCESSING ---
        self.processing_queue = queue.Queue(maxsize=1) # Raw frames for processing
        self.display_queue = queue.Queue(maxsize=1)    # Processed CTkImages for display
        self.processing_thread = None
        self.stop_processing_event = threading.Event()

    def set_enable_overlays(self, value: bool):
        """Enable or disable drawing overlays for performance."""
        self.enable_overlays = value

    def start_capture(self):
        print("Starting video capture...")
        if self.view_model:
            self.cap = cv2.VideoCapture(self.view_model.camera_index)
        else:
            self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.cap.isOpened():
            self.set_overlay_text("Error: Cannot open camera.")
            return
        self.set_overlay_text("") # Clear initial text

        # Start the image processing thread
        self.stop_processing_event.clear()
        self.processing_thread = threading.Thread(target=self._image_processing_worker, daemon=True)
        self.processing_thread.start()

        self._update_frame() # Start the UI update loop

    def stop_capture(self):
        if self.cap:
            self.cap.release()
        self.cap = None
        self.last_frame = None
        self.label_widget.configure(image=None)
        self.set_overlay_text("Camera Off")
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        
        # Stop the image processing thread
        self.stop_processing_event.set()
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0) # Wait for thread to finish

    def set_recognized_faces(self, faces_with_status):
        """
        A method to pass recognized face data with status.
        faces_with_status is a list of tuples: (name, location, status)
        """
        self.faces_with_status = faces_with_status

    def _image_processing_worker(self):
        while not self.stop_processing_event.is_set():
            try:
                # Get raw frame from the processing queue (blocking with timeout)
                frame = self.processing_queue.get(timeout=0.1) 
                
                # Perform image processing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                # Get widget dimensions (from main thread, might be slightly outdated but acceptable)
                widget_w, widget_h = self.winfo_width(), self.winfo_height()
                img_w, img_h = img.size

                # Define a maximum internal rendering resolution for the video feed
                MAX_RENDER_WIDTH = 1920
                MAX_RENDER_HEIGHT = 1080

                # Calculate scaling ratio to fit within widget AND max render resolution
                ratio_widget = min(widget_w / img_w, widget_h / img_h) if img_w > 0 and img_h > 0 else 0
                
                # Calculate ratio to fit within max render resolution
                ratio_max_render = min(MAX_RENDER_WIDTH / img_w, MAX_RENDER_HEIGHT / img_h) if img_w > 0 and img_h > 0 else 0

                # Use the smaller of the two ratios to ensure we don't exceed max render resolution
                # and still fit within the widget
                final_ratio = min(ratio_widget, ratio_max_render)

                new_w, new_h = int(img_w * final_ratio), int(img_h * final_ratio)

                if new_w > 0 and new_h > 0:
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, size=(new_w, new_h))
                    
                    # Put processed image into display queue
                    try:
                        self.display_queue.put_nowait(photo)
                    except queue.Full:
                        pass # Skip if queue is full (UI is not consuming fast enough)
            except queue.Empty:
                pass # No frame to process, continue loop
            except Exception as e:
                print(f"Image processing worker error: {e}")
                # Optionally, log the error or set a flag to stop the worker

    def _update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.last_frame = frame.copy() # Store raw frame for get_frame()

                # --- Draw overlays on the frame before sending to processing thread ---
                if self.enable_overlays:
                    faces_to_draw = self.faces_with_status if hasattr(self, 'faces_with_status') and self.faces_with_status else []
                    frame_h, frame_w = frame.shape[:2]
                    for name, (top, right, bottom, left), status, course, class_name, match_percent in faces_to_draw:
                        display_lines = []
                        box_color = (0, 0, 255) # Default Red for Unknown

                        student_id = name.split('_')[0] if '_' in name else "N/A"
                        raw_name = name.split('_')[1] if '_' in name and len(name.split('_')) > 1 else name

                        # Format match percent as integer percentage string if present
                        match_percent_str = f"Match: {int(round(match_percent))}%" if match_percent is not None else None

                        if status == "Attended":
                            box_color = (237, 107, 29) # FPT Orange
                            display_lines.append("ATTENDED")
                            display_lines.append(f"Name: {raw_name}")
                            display_lines.append(f"ID: {student_id}")
                            display_lines.append(f"{course} - {class_name}")
                        elif status == "Already Logged":
                            box_color = (52, 152, 219) # Blue for Info/Already Logged
                            display_lines.append("ALREADY LOGGED")
                            display_lines.append(f"Name: {raw_name}")
                            display_lines.append(f"ID: {student_id}")
                            display_lines.append(f"{course} - {class_name}")
                        elif "Verifying" in status:
                            box_color = (241, 196, 15) # Yellow
                            display_lines.append(status.upper())
                            display_lines.append(f"Name: {raw_name}")
                            display_lines.append(f"ID: {student_id}")
                        elif status == "Known":
                            box_color = (0, 255, 0) # Green
                            display_lines.append("KNOWN")
                            display_lines.append(f"Name: {raw_name}")
                            display_lines.append(f"ID: {student_id}")
                        else: # Unknown
                            box_color = (0, 0, 255) # Red
                            display_lines.append("UNKNOWN")

                        # Draw bounding box (thicker, rounded corners)
                        thickness = 2
                        cv2.rectangle(frame, (left, top), (right, bottom), box_color, thickness, lineType=cv2.LINE_AA)
                        for pt in [(left, top), (right, top), (left, bottom), (right, bottom)]:
                            cv2.circle(frame, pt, 6, box_color, -1, lineType=cv2.LINE_AA)

                        # --- Beautified Label: Dynamic width, right-align match percent, no overshoot, full text ---
                        font_scale = 0.6
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        label_padding = 8
                        line_height = 0
                        label_lines = []
                        max_text_width = 0
                        for idx, line in enumerate(display_lines):
                            # If this is the last line and match_percent_str exists, add space for it
                            if idx == len(display_lines) - 1 and match_percent_str:
                                # Calculate width for line + match_percent_str with a gap
                                (text_width, text_height), _ = cv2.getTextSize(line + "    " + match_percent_str, font, font_scale, 1)
                            else:
                                (text_width, text_height), _ = cv2.getTextSize(line, font, font_scale, 1)
                            max_text_width = max(max_text_width, text_width)
                            label_lines.append(line)
                            line_height = max(line_height, text_height)
                        label_width = max(right - left, max_text_width + 2 * label_padding)
                        label_height = (line_height + 6) * len(label_lines) + 2 * label_padding
                        # Center label above bounding box, keep within frame
                        label_left = max(left + (right - left)//2 - label_width//2, 0)
                        label_right = min(label_left + label_width, frame_w)
                        label_top = max(top - label_height - 10, 0)
                        label_bottom = top - 10
                        # Draw filled rectangle
                        cv2.rectangle(frame, (label_left, label_top), (label_right, label_bottom), box_color, cv2.FILLED, lineType=cv2.LINE_AA)
                        # Draw border
                        cv2.rectangle(frame, (label_left, label_top), (label_right, label_bottom), (255,255,255), 1, lineType=cv2.LINE_AA)
                        # Draw text lines, right-align match percent if present on last line
                        y = label_top + label_padding + line_height
                        for idx, line in enumerate(label_lines):
                            (text_width, text_height), _ = cv2.getTextSize(line, font, font_scale, 1)
                            x = label_left + label_padding
                            if idx == len(label_lines) - 1 and match_percent_str:
                                # Draw line left, match percent right
                                cv2.putText(frame, line, (x, y), font, font_scale, (255,255,255), 1, cv2.LINE_AA)
                                # Calculate right-aligned x for match percent
                                (mp_width, _), _ = cv2.getTextSize(match_percent_str, font, font_scale, 1)
                                mp_x = label_right - label_padding - mp_width
                                cv2.putText(frame, match_percent_str, (mp_x, y), font, font_scale, (255,255,255), 1, cv2.LINE_AA)
                            else:
                                cv2.putText(frame, line, (x, y), font, font_scale, (255,255,255), 1, cv2.LINE_AA)
                            y += line_height + 6

                # Put the frame (with or without overlays) into the processing queue
                try:
                    self.processing_queue.put_nowait(frame)
                except queue.Full:
                    pass # Skip if processing queue is full

                # Try to get a processed image from the display queue
                try:
                    photo = self.display_queue.get_nowait()
                    self.label_widget.configure(image=photo, text="")
                    self.label_widget.image = photo
                except queue.Empty:
                    pass # No new image to display yet

        if self.cap and self.cap.isOpened():
            self._after_id = self.after(30, self._update_frame) # Schedule next UI update

    # --- NEW PUBLIC METHODS ---
    def get_frame(self):
        """Returns the last captured raw cv2 frame."""
        return self.last_frame
        
    def set_overlay_text(self, text, duration_ms=None):
        """
        Updates the step prompt (top) or shows a warning (center).
        If duration_ms is provided, shows the warning in the center, then hides it.
        Otherwise, updates the persistent step prompt at the top.
        """
        if not hasattr(self, "_persistent_overlay_text"):
            self._persistent_overlay_text = ""
        if duration_ms is None:
            # Set persistent overlay (step prompt at top)
            self._persistent_overlay_text = text
            self.overlay_label.configure(text=text)
            if hasattr(self, "_overlay_clear_after_id") and self._overlay_clear_after_id:
                self.after_cancel(self._overlay_clear_after_id)
                self._overlay_clear_after_id = None
        else:
            # Show warning overlay in center, then hide it
            self.overlay_warning_label.lift()
            self.overlay_warning_label.configure(text=text)
            if hasattr(self, "_warning_overlay_clear_after_id") and self._warning_overlay_clear_after_id:
                self.after_cancel(self._warning_overlay_clear_after_id)
            def hide_warning():
                self.overlay_warning_label.configure(text="")
                self.overlay_warning_label.lower()
            self._warning_overlay_clear_after_id = self.after(duration_ms, hide_warning)
        
    def set_progress_overlay_text(self, text):
        """Updates the text on the progress overlay label persistently (does not auto-clear)."""
        self.overlay_progress_label.configure(text=text)
        # Remove any scheduled auto-clear
        if hasattr(self, "_progress_overlay_clear_after_id") and self._progress_overlay_clear_after_id:
            self.after_cancel(self._progress_overlay_clear_after_id)
            self._progress_overlay_clear_after_id = None

    def flash_effect(self):
        """Creates a brief flash effect on the widget."""
        original_color = self.cget("fg_color")
        self.configure(fg_color="white")
        self.after(50, lambda: self.configure(fg_color=original_color))