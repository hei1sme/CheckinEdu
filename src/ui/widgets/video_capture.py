import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

class VideoCapture(ctk.CTkFrame):
    def __init__(self, parent, initial_text=""):
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
        self.last_frame = None

    def start_capture(self):
        # Placeholder for starting the camera
        print("Starting video capture...")
        self.cap = cv2.VideoCapture(0)
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

    def _update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # --- NEW: FLIP THE FRAME HORIZONTALLY ---
                frame = cv2.flip(frame, 1)
                
                self.last_frame = frame.copy() # Store the raw cv2 frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                widget_w, widget_h = self.winfo_width(), self.winfo_height()
                img_w, img_h = img.size
                ratio = min(widget_w/img_w, widget_h/img_h) if img_w > 0 and img_h > 0 else 0
                new_w, new_h = int(img_w * ratio), int(img_h * ratio)
                if new_w > 0 and new_h > 0:
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=img)
                    self.label_widget.configure(image=photo, text="")
                    self.label_widget.image = photo
            self.after(15, self._update_frame)

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