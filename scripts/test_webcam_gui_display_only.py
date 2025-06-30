import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import customtkinter as ctk
from src.ui.widgets.video_capture import VideoCapture

class DisplayOnlyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Webcam Display Only (GUI Test)")
        self.geometry("900x700")
        self.resizable(False, False)

        self.video_frame = VideoCapture(self, initial_text="Display Only Mode")
        self.video_frame.pack(expand=True, fill="both", padx=24, pady=24)
        self.video_frame.set_enable_overlays(False)
        self.video_frame.start_capture()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.video_frame.stop_capture()
        self.destroy()

if __name__ == "__main__":
    app = DisplayOnlyApp()
    app.mainloop()