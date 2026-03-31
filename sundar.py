import cv2
import time
import platform
import pyttsx3
import ctypes
import os
import tkinter as tk
from PIL import Image, ImageTk

class PulmoLock:
    def __init__(self, window):
        self.window = window
        self.window.title("PulmoLock - Full Screen Monitor")
        
        # --- FULLSCREEN SETTINGS ---
        self.window.attributes("-fullscreen", True)
        self.window.configure(bg="black")
        
        # Get your monitor's exact resolution
        self.screen_w = self.window.winfo_screenwidth()
        self.screen_h = self.window.winfo_screenheight()

        # ESC key to exit
        self.window.bind("<Escape>", lambda e: self.close_app())

        # --- Variables ---
        self.is_monitoring = False
        self.wait_time = 12  
        self.last_seen_time = time.time()
        self.cap = None
        self.engine = pyttsx3.init()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.setup_ui()

    def setup_ui(self):
        # 1. Video Background (Fills 100% of the screen)
        self.video_label = tk.Label(self.window, bg="black")
        self.video_label.place(x=0, y=0, width=self.screen_w, height=self.screen_h)

        # 2. UI Overlay (Floating on top of the video)
        self.overlay_frame = tk.Frame(self.window, bg="", bd=0)
        self.overlay_frame.place(relx=0.5, rely=0.9, anchor="center")

        self.status_var = tk.StringVar(value="SYSTEM READY")
        self.status_label = tk.Label(
            self.window, textvariable=self.status_var,
            font=("Helvetica", 24, "bold"), fg="#00ffcc", bg="black"
        )
        self.status_label.place(relx=0.5, rely=0.1, anchor="center")

        self.btn_toggle = tk.Button(
            self.overlay_frame, text="START PULMOLOCK", 
            font=("Arial", 14, "bold"), bg="#00ffcc", fg="black",
            command=self.toggle_system, padx=20, pady=10
        )
        self.btn_toggle.pack()

    def close_app(self):
        self.is_monitoring = False
        if self.cap:
            self.cap.release()
        self.window.destroy()

    def toggle_system(self):
        if not self.is_monitoring:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.is_monitoring = True
            self.last_seen_time = time.time()
            self.btn_toggle.config(text="STOP (ESC)", bg="#ff4b2b", fg="white")
            self.update_loop()
        else:
            self.close_app()

    def update_loop(self):
        if not self.is_monitoring: return

        ret, frame = self.cap.read()
        if ret:
            # AI Logic
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                self.last_seen_time = time.time()
                self.status_var.set("USER PRESENT")
                self.status_label.config(fg="#00ffcc")
            else:
                elapsed = time.time() - self.last_seen_time
                count = max(0, int(self.wait_time - elapsed))
                self.status_var.set(f"ABSENCE DETECTED: {count}s")
                self.status_label.config(fg="#ff4b2b")

                if elapsed > self.wait_time:
                    self.execute_sleep()
                    return

            # Full Screen UI Processing
            frame = cv2.flip(frame, 1) # Mirror mode
            frame = cv2.resize(frame, (self.screen_w, self.screen_h)) # Stretch to screen
            
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(10, self.update_loop)

    def execute_sleep(self):
        self.engine.say("Suspending system.")
        self.engine.runAndWait()
        self.close_app()
        if platform.system() == "Windows":
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        else:
            os.system("systemctl suspend")

if __name__ == "__main__":
    root = tk.Tk()
    app = PulmoLock(root)
    root.mainloop()
