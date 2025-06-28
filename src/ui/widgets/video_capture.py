import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

class VideoCapture(ctk.CTkFrame):
    def __init__(self, parent, initial_text="", view_model=None):
        super().__init__(parent, fg_color="black")
        self.label_widget = ctk.CTkLabel(self, text="", image=None)
        self.label_widget.pack(expand=True, fill="both")
        
        # --- OVERLAY for instructions ---
        self.overlay_label = ctk.CTkLabel(
            self, text=initial_text,
            font=ctk.CTkFont(family="Poppins", size=20, weight="bold"),
            fg_color="black", text_color="white"
        )
        self.overlay_label.place(relx=0.5, rely=0.1, anchor="center")
        
        self.cap = None
        self.view_model = view_model
        self.last_frame = None
        self.faces_with_status = [] # Initialize faces_with_status
        self._after_id = None # To store the ID of the scheduled after call

    def start_capture(self):
        # Placeholder for starting the camera
        print("Starting video capture...")
        if self.view_model:
            self.cap = cv2.VideoCapture(self.view_model.camera_index)
        else:
            self.cap = cv2.VideoCapture(0)
        # Set camera resolution for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.cap.isOpened():
            self.set_overlay_text("Error: Cannot open camera.")
            return
        self.set_overlay_text("") # Clear initial text
        self._update_frame()
        
    def stop_capture(self):
        if self.cap:
            self.cap.release()
        self.cap = None
        self.last_frame = None
        self.label_widget.configure(image=None)
        self.set_overlay_text("Camera Off")
        if self._after_id: # Cancel any pending _update_frame calls
            self.after_cancel(self._after_id)
            self._after_id = None

    def set_recognized_faces(self, faces_with_status):
        """
        A method to pass recognized face data with status.
        faces_with_status is a list of tuples: (name, location, status)
        """
        self.faces_with_status = faces_with_status

    def _update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                # --- Always draw last known faces, even if not updated this frame ---
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

                self.last_frame = frame.copy()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                widget_w, widget_h = self.winfo_width(), self.winfo_height()
                img_w, img_h = img.size
                ratio = min(widget_w/img_w, widget_h/img_h) if img_w > 0 and img_h > 0 else 0
                new_w, new_h = int(img_w * ratio), int(img_h * ratio)
                if new_w > 0 and new_h > 0:
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, size=(new_w, new_h))
                    self.label_widget.configure(image=photo, text="")
                    self.label_widget.image = photo
        if self.cap and self.cap.isOpened():
            self._after_id = self.after(15, self._update_frame)

    # --- NEW PUBLIC METHODS ---
    def get_frame(self):
        """Returns the last captured raw cv2 frame."""
        return self.last_frame
        
    def set_overlay_text(self, text):
        """Updates the text on the overlay label."""
        self.overlay_label.configure(text=text)
        
    def flash_effect(self):
        """Creates a brief flash effect on the widget."""
        original_color = self.cget("fg_color")
        self.configure(fg_color="white")
        self.after(50, lambda: self.configure(fg_color=original_color))