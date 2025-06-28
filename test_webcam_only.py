import customtkinter as ctk
from src.ui.widgets.video_capture import VideoCapture

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Webcam Test")
        self.geometry("800x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.video_capture = VideoCapture(self)
        self.video_capture.grid(row=0, column=0, sticky="nsew")
        self.video_capture.start_capture()

    def on_closing(self):
        self.video_capture.stop_capture()
        self.destroy()

if __name__ == "__main__":
    app = TestApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()