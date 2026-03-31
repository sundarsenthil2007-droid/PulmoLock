import cv2
import time
import platform
import pyttsx3
import ctypes
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PresenceApp:
    def __init__(self, window):
        self.window = window
        self.window.title("AI Presence Lock")
        self.window.geometry("700x600")
        self.window.configure(bg="#2c3e50")

        # --- Variables ---
        self.running = False
        self.wait_time = 10
        self.last_seen_time = time.time()
        self.cap = None
        self.engine = pyttsx3.init()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # --- UI Layout ---
        self.setup_ui()

    def setup_ui(self):
        # Title
        title = tk.Label(self.window, text="Presence Monitor", font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=10)

        # Video Feed Label
        self.video_label = tk.Label(self.window, bg="black")
        self.video_label.pack(pady=10, padx=20)

        # Status & Countdown
        self.status_label = tk.Label(self.window, text="Status: Idle", font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
        self.status_label.pack(pady=5)

        # Control Button
        self.btn_toggle = ttk.Button(self.window, text="Start Monitoring", command=self.toggle_monitoring)
        self.btn_toggle.pack(pady=20)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def suspend_pc(self):
        self.speak("No face detected. Suspending system.")
        if platform.system() == "Windows":
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        else:
            import os
            os.system("systemctl suspend")

    def toggle_monitoring(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.status_label.config(text="Error: Camera not found", fg="#e74c3c")
                return
            self.running = True
            self.last_seen_time = time.time()
            self.btn_toggle.config(text="Stop Monitoring")
            self.update_frame()
        else:
            self.stop_monitoring()

    def stop_monitoring(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image="")
        self.btn_toggle.config(text="Start Monitoring")
        self.status_label.config(text="Status: Idle", fg="#ecf0f1")

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Face Detection Logic
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                self.last_seen_time = time.time()
                self.status_label.config(text="Status: User Present", fg="#2ecc71")
            else:
                elapsed = time.time() - self.last_seen_time
                seconds_left = max(0, int(self.wait_time - elapsed))
                self.status_label.config(text=f"Status: Away - Sleeping in {seconds_left}s", fg="#e67e22")

                if elapsed > self.wait_time:
                    self.stop_monitoring()
                    self.suspend_pc()
                    return

            # Convert OpenCV frame (BGR) to Tkinter compatible image (RGB)
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Repeat every 10ms
        self.window.after(10, self.update_frame)

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = PresenceApp(root)
    root.mainloop()