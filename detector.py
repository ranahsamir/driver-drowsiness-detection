import cv2
import dlib
from scipy.spatial import distance
import time
import threading
import config
import serial
from telegram_alert_message import send_drowsiness_alert
from telegram_with_pic import send_telegram_photo
from datetime import datetime

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

class Detector:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.eye_counter = 0
        self.last_alert_time = 0

        # Connect to Arduino
        try:
            self.arduino = serial.Serial(config.ARDUINO_PORT, config.BAUD, timeout=1)
            time.sleep(2)
        except Exception as e:
            print(f"Serial Error: {e}")
            self.arduino = None

        self.last_state = '0'

    def send_to_arduino(self, state):
        if self.arduino and state != self.last_state:
            self.arduino.write(state.encode())
            self.last_state = state

    def analyze(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        ear_value = 0
        state = '0'

        # Reset counter if no face is detected to avoid lag in state change
        if len(faces) == 0:
            self.eye_counter = 0

        for face in faces:
            landmarks = self.predictor(gray, face)

            # Extract eye coordinates
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

            # Calculate EAR
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
            ear_value = round(ear, 2)

            # State Logic
            if ear < config.EAR_THRESHOLD:
                self.eye_counter += 1
            else:
                self.eye_counter = 0

            # Draw for visual feedback
            color = (0, 255, 0) if self.eye_counter <= 25 else (0, 0, 255)
            cv2.putText(frame, f"EAR: {ear_value}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Determine state
        state = '1' if self.eye_counter > 25 else '0'
        self.send_to_arduino(state)

        # Alert Logic
        if state == '1':
            current_time = time.time()
            if current_time - self.last_alert_time > 15:
                self.last_alert_time = current_time
                # Taking a snapshot for the thread to use
                cv2.imwrite("driver_alert.jpg", frame)
                threading.Thread(target=send_drowsiness_alert).start()
                threading.Thread(target=send_telegram_photo,
                                 args=("driver_alert.jpg", "⚠️ Driver is sleeping!")).start()

                current_time_str = datetime.now().strftime("%Y%m%d-%H%M%S")
                img_name = f"static/alerts/alert_{current_time_str}.jpg"
                cv2.imwrite(img_name, frame)

        return state, ear_value
