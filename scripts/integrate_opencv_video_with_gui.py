import customtkinter as ctk
import threading
import cv2

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CheckinEdu (Hybrid OpenCV Video)")
        self.geometry("400x200")
        self.resizable(False, False)

        self.running = False
        self.capture_thread = None

        self.start_button = ctk.CTkButton(self, text="Start Video Feed", command=self.start_video)
        self.start_button.pack(pady=20)

        self.stop_button = ctk.CTkButton(self, text="Stop Video Feed", command=self.stop_video, state="disabled")
        self.stop_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Status: Idle")
        self.status_label.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_video(self):
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.capture_thread.start()
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Status: Video Running")

    def stop_video(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Idle")

    def video_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            self.status_label.configure(text="Status: Camera Error")
            return
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            # Here you can add face detection/recognition and draw overlays on 'frame'
            cv2.imshow("CheckinEdu Video Feed (OpenCV)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break
        cap.release()
        cv2.destroyAllWindows()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Idle")

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()