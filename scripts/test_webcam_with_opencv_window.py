import customtkinter as ctk
import threading
import cv2

class ControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Control Panel (OpenCV Video Window)")
        self.geometry("400x200")
        self.resizable(False, False)

        self.running = False
        self.capture_thread = None

        self.start_button = ctk.CTkButton(self, text="Start Webcam", command=self.start_webcam)
        self.start_button.pack(pady=20)

        self.stop_button = ctk.CTkButton(self, text="Stop Webcam", command=self.stop_webcam, state="disabled")
        self.stop_button.pack(pady=20)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_webcam(self):
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(target=self.webcam_loop, daemon=True)
            self.capture_thread.start()
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")

    def stop_webcam(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def webcam_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("OpenCV Video Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break
        cap.release()
        cv2.destroyAllWindows()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = ControlApp()
    app.mainloop()